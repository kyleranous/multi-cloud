# MultiCloud.yaml


```yaml
# MultiCloud Function Configuration File

# Optional configuration settings are commented out by default

# Function metadata
name: hello-world
description: "Example Hello World Function"
version: 1.0.0  # Function Version

# Function authors, Multiple OK
authors:
  - name: First Last
    email: my_email@test.com

# Methods and Dependecies
handler: hello-world.handler # Handler method called by provider specific entry points
requirements: path/to/requirements.txt
readme: path/to/README.md
#license: MIT # License is optional

# Environment Variables\\\\\
environment:
  key: value

# Platform specific settings
# All previous settings can be overridden on a per platform basis here.
platforms:
  - name: knative
    version: 0.36.0
```