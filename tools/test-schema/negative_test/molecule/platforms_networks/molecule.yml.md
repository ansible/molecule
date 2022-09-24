# ajv errors

```json
[
  {
    "instancePath": "/platforms/0/networks/0",
    "keyword": "type",
    "message": "must be object",
    "params": {
      "type": "object"
    },
    "schemaPath": "#/$defs/platform-network/type"
  },
  {
    "instancePath": "/platforms/0/networks/1",
    "keyword": "type",
    "message": "must be object",
    "params": {
      "type": "object"
    },
    "schemaPath": "#/$defs/platform-network/type"
  }
]
```

# check-jsonschema

stdout:

```json
{
  "status": "fail",
  "errors": [
    {
      "filename": "negative_test/molecule/platforms_networks/molecule.yml",
      "path": "$.platforms[0].networks[0]",
      "message": "'foo' is not of type 'object'",
      "has_sub_errors": false
    },
    {
      "filename": "negative_test/molecule/platforms_networks/molecule.yml",
      "path": "$.platforms[0].networks[1]",
      "message": "'bar' is not of type 'object'",
      "has_sub_errors": false
    }
  ],
  "parse_errors": []
}
```
