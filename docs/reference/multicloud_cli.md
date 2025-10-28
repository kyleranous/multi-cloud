# MultiCloud CLI Documentation

The MultiCloud CLI helps you scaffold, validate, and deploy serverless functions across multiple cloud platforms.

## Installation

MultiCloud CLI is installed with the package.

## Usage

Run the CLI with:

```bash
multicloud [COMMAND] [OPTIONS]
```

## Commands

| Command         | Description                                      |
|-----------------|--------------------------------------------------|
| `init`          | Initialize a new MultiCloud project              |
| `scaffold`      | Scaffold a new function for a target platform    |
| `validate`      | Validate your function and configuration         |
| `config`        | View or edit project configuration               |
| `help`          | Show help for any command                        |

## Examples

### Initialize a New Project

```bash
multicloud init
```

### Scaffold a New Function

```bash
multicloud scaffold --name hello_world --platform aws
```

### Validate Your Project

```bash
multicloud validate
```


## Configuration

The CLI uses `.multicloud/config.yaml` for project settings. Example:

```yaml
author:
  email: your@email.com
  name: Your Name
defaults:
  runtime: python
  memory: 128Mi
  timeout: 30s
  log_level: INFO
platforms:
  aws: {}
  azure: {}
  gcp: {}
  knative: {}
```

### Initialize a configuration file
Guided setup of `.multicloud/config.yaml`
```bash
multicloud config init
```

## Help

For more information on a command, use:

```bash
multicloud [COMMAND] --help
```