# EnvCheck 🔐

A small, dependency-free Python CLI that verifies whether required environment variables are set without printing their values.

It is designed for troubleshooting application configuration safely, especially when environment variables may contain API keys, tokens, credentials, or connection strings.

## Quick start

Create a `.env.example` file that lists the variables your application expects:

```dotenv
DATABASE_URL=
API_BASE_URL=https://api.example.com
STRIPE_API_KEY=
LOG_LEVEL=info # optional
DEBUG_MODE=false # optional
```

Then run:

```bash
python3 envcheck.py
```

EnvCheck checks the current process environment. Values written in `.env.example` are treated only as documentation and are never loaded as runtime secrets.

## Example output

```text
ENVCHECK
──────────────────────────────────────────────────────
✓ DATABASE_URL                   SET
✓ API_BASE_URL                   SET
✗ STRIPE_API_KEY                 MISSING
○ LOG_LEVEL                      OPTIONAL / MISSING
○ DEBUG_MODE                     OPTIONAL / MISSING
──────────────────────────────────────────────────────
2 set • 1 missing • 2 optional missing

✗ Environment is not ready.
```

## Marking variables optional

Add `# optional` to the same line:

```dotenv
DEBUG=false # optional
```

Optional variables are reported but do not cause a failed exit code.

## JSON output

```bash
python3 envcheck.py --json
```

The JSON response contains variable names and states only. Secret values are never included.

## Custom spec file

```bash
python3 envcheck.py config/production.env.example
```

## Exit codes

- `0` when every required variable is set
- `1` when one or more required variables are missing
- argparse reports malformed or unreadable spec files

This makes EnvCheck useful in local scripts and CI workflows.

## Security approach

EnvCheck intentionally answers only one question: is the variable set?

It does not print, log, serialize, mask, hash, or otherwise expose the value. The checker also does not load secrets from `.env` files.

## Tests

```bash
python3 -m unittest -v
```

The test suite includes a check confirming that a secret value passed to the checker never appears in its returned result.

## Roadmap

- Variable groups for different services
- Prefix-based checks
- Multiple environment profiles
- Optional format validation without exposing values
- GitHub Actions example

## License

MIT
