# ajv errors

```json
[
  {
    "instancePath": "/platforms/0/children",
    "keyword": "type",
    "message": "must be array",
    "params": {
      "type": "array"
    },
    "schemaPath": "#/properties/children/type"
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
      "filename": "negative_test/molecule/platforms_children/molecule.yml",
      "path": "$.platforms[0].children",
      "message": "2 is not of type 'array'",
      "has_sub_errors": false
    }
  ],
  "parse_errors": []
}
```
