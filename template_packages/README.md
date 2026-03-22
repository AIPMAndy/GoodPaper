# Template Packages

Each package lives in its own folder and contains a `manifest.json`.

Required manifest fields:

- `package_id`
- `name`
- `template_file`

Optional fields:

- `description`
- `version`
- `default`
- `semantic_styles`

Example workflow:

1. Copy a new template into a package folder.
2. Add a `manifest.json`.
3. Restart the local server or rerun a CLI command.

The current MVP still derives most validation rules from the Word template itself.
