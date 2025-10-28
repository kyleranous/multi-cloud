# MultiCloud
MultiCloud is a framework to assist in developing and deploying serverless functions across multiple cloud platforms.


[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


## Features

- **Multi-Cloud Support**: Deploy the same function to Knative, AWS Lambda(Planned), Azure Functions(Planned), and Google Cloud(Planned)
-**Unified Event Model**: Consistent `MultiCouldEvent` interface across all platforms
-**CLI Tools**: Command-line interface for scaffolding, validation, and deployment
- **Template System**: Generate platform-specific code from templates
- **Type Safety**: Full type hints and static analysis support

## Installation

```bash
pip install git+https://github.com/kyleranous/multi-cloud.git@v0.1.0
```

Development Installation
```bash
git clone https://github.com/yourusername/multi-cloud.git
cd multi-cloud
pip install -e ".[dev]"
```

## Usage
### CLI COmmands
The MultiCloud CLI provides several commands for working with serverless functions:

In Progress

## Supported Python Versions
| Version        | Planned | Tested |
| :------        | :-----: | :----: |
| 3.10 and below | ❌      | ❌     |
| 3.11           | ✅      | 🧪     |
| 3.12           | ✅      | 🧪     |
| 3.13           | ✅      | 🧪     |
| 3.14           | ✅      | 🧪     |

Legend:
- ✅ Supported
- 🧪 Testing in progress  
- 📋 Planned for testing

## Supported Platforms
| Platform               | Status            |
| :-------               | :-----            |
| Knative                | 🚧 In Development |
| AWS Lambda             | 📋 Planned        |
| Azure Functions        | 📋 Planned        |
| Google Cloud Functions | 📋 Planned        |
| SpinKube               | 🔍 Investigating  |
| OpenFaaS               | 🔍 Investigating  |

## Contributing
Quick Contribution Steps
1. Review all documentation
2. Fork the repository
3. Create a feature branch (`git checkout -b feature/new-feature`)
4. Make the changes
5. Add tests for new functionality
6. Run the test suite (`pytest`)
7. Commit your changes (`git commit -m 'Valid commit message here`)
8. Push to the branch (`git push origin feature/new-feature`)
9. Open a Pull Request

## Documentation
- [API Documentation](docs/api/api.md)
- [Style Guide](docs/styleguide.md)
- [Change Log](CHANGELOG.md)