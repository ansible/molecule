import * as path from "path";
import Ajv from "ajv";
import fs from "fs";
import minimatch from "minimatch";
import yaml from "js-yaml";
import { assert } from "chai";
import stringify from "safe-stable-stringify";
import { integer } from "vscode-languageserver-types";
import { exec } from "child_process";
const spawnSync = require("child_process").spawnSync;

function ansiRegex({ onlyFirst = false } = {}) {
  const pattern = [
    "[\\u001B\\u009B][[\\]()#;?]*(?:(?:(?:(?:;[-a-zA-Z\\d\\/#&.:=?%@~_]+)*|[a-zA-Z\\d]+(?:;[-a-zA-Z\\d\\/#&.:=?%@~_]*)*)?\\u0007)",
    "(?:(?:\\d{1,4}(?:;\\d{0,4})*)?[\\dA-PR-TZcf-nq-uy=><~]))",
  ].join("|");

  return new RegExp(pattern, onlyFirst ? undefined : "g");
}

function stripAnsi(data: string) {
  if (typeof data !== "string") {
    throw new TypeError(
      `Expected a \`string\`, got \`${typeof data}\ = ${data}`
    );
  }
  return data.replace(ansiRegex(), "");
}

const ajv = new Ajv({
  strictTypes: false,
  strict: false,
  inlineRefs: true, // https://github.com/ajv-validator/ajv/issues/1581#issuecomment-832211568
  allErrors: true, // https://github.com/ajv-validator/ajv/issues/1581#issuecomment-832211568
});

// load whitelist of all test file subjects schemas can reference
const test_files = getAllFiles("./test");
const negative_test_files = getAllFiles("./negative_test");

// load all schemas
const schema_files = fs
  .readdirSync("f/")
  .filter((el) => path.extname(el) === ".json");
console.log(`Schemas: ${schema_files}`);

describe("schemas under f/", function () {
  schema_files.forEach((schema_file) => {
    const schema_json = JSON.parse(fs.readFileSync(`f/${schema_file}`, "utf8"));
    ajv.addSchema(schema_json);
    const validator = ajv.compile(schema_json);
    if (schema_json.examples == undefined) {
      console.error(
        `Schema file ${schema_file} is missing an examples key that we need for documenting file matching patterns.`
      );
      return process.exit(1);
    }
    describe(schema_file, function () {
      getTestFiles(schema_json.examples).forEach(
        ({ file: test_file, expect_fail }) => {
          it(`linting ${test_file} using ${schema_file}`, function () {
            var errors_md = "";
            const result = validator(
              yaml.load(fs.readFileSync(test_file, "utf8"))
            );
            if (validator.errors) {
              errors_md += "# ajv errors\n\n```json\n";
              errors_md += stringify(validator.errors, null, 2);
              errors_md += "\n```\n\n";
            }
            // validate using check-jsonschema (python-jsonschema):
            // const py = exec();
            // Do not use python -m ... calling notation because for some
            // reason, nodejs environment lacks some env variables needed
            // and breaks usage from inside virtualenvs.
            const proc = spawnSync(
              `check-jsonschema -v -o json --schemafile f/${schema_file} ${test_file}`,
              { shell: true, encoding: "utf-8", stdio: "pipe" }
            );
            if (proc.status != 0) {
              // real errors are sent to stderr due to https://github.com/python-jsonschema/check-jsonschema/issues/88
              errors_md += "# check-jsonschema\n\nstdout:\n\n```json\n";
              errors_md += stripAnsi(proc.output[1]);
              errors_md += "```\n";
              if (proc.output[2]) {
                errors_md += "\nstderr:\n\n```\n";
                errors_md += stripAnsi(proc.output[2]);
                errors_md += "```\n";
              }
            }

            // dump errors to markdown file for manual inspection
            const md_filename = `${test_file}.md`;
            if (errors_md) {
              fs.writeFileSync(md_filename, errors_md);
            } else {
              // if no error occurs, we should ensure there is no md file present
              fs.unlink(md_filename, function (err) {
                if (err && err.code != "ENOENT") {
                  console.error(`Failed to remove ${md_filename}.`);
                }
              });
            }
            assert.equal(
              result,
              !expect_fail,
              `${JSON.stringify(validator.errors)}`
            );
          });
        }
      );
      // All /$defs/ that have examples property are assumed to be
      // subschemas, "tasks" being the primary such case, which is also used
      // for validating separated files.
      for (var definition in schema_json["$defs"]) {
        if (schema_json["$defs"][definition].examples) {
          const subschema_uri = `${schema_json["$id"]}#/$defs/${definition}`;
          const subschema_validator = ajv.getSchema(subschema_uri);
          if (!subschema_validator) {
            console.error(`Failed to load subschema ${subschema_uri}`);
            return process.exit(1);
          }
          getTestFiles(schema_json["$defs"][definition].examples).forEach(
            ({ file: test_file, expect_fail }) => {
              it(`linting ${test_file} using ${subschema_uri}`, function () {
                const result = subschema_validator(
                  yaml.load(fs.readFileSync(test_file, "utf8"))
                );
                assert.equal(
                  result,
                  !expect_fail,
                  `${JSON.stringify(validator.errors)}`
                );
              });
            }
          );
        }
      }
    });
  });
});

// find all tests for each schema file
function getTestFiles(
  globs: string[]
): { file: string; expect_fail: boolean }[] {
  const files = Array.from(
    new Set(
      globs
        .map((glob: any) => minimatch.match(test_files, path.join("**", glob)))
        .flat()
    )
  );
  const negative_files = Array.from(
    new Set(
      globs
        .map((glob: any) =>
          minimatch.match(negative_test_files, path.join("**", glob))
        )
        .flat()
    )
  );

  // All fails ending with fail, like `foo.fail.yml` are expected to fail validation
  let result = files.map((f) => ({ file: f, expect_fail: false }));
  result = result.concat(
    negative_files.map((f) => ({ file: f, expect_fail: true }))
  );
  return result;
}

function getAllFiles(dir: string): string[] {
  return fs.readdirSync(dir).reduce((files: string[], file: string) => {
    const name = path.join(dir, file);
    const isDirectory = fs.statSync(name).isDirectory();
    return isDirectory ? [...files, ...getAllFiles(name)] : [...files, name];
  }, []);
}
