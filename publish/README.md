### Development of containers, services, policies and defintion files

#### Using a shared IEAM environment to Build and Publish serrvices 

Using a shared single tenant instance creates several challenges when services, patterns and policies need to be published in a common exchange under one org without multiple developers clobbering over each other.

#### Issues

- Developers need to identify their service, pattern and policies among many similar assets (concept of owner)
- Developers may have project for demo, dev, test and more ( group the assets)
- Developers need to use their own docker repository (specify own docker account)

The tooling outlined below addresses these concerns and builds on top of existing infrastructure

### Automated Steps

Start with reviewing Makefile for targets.

### Setup ENVIRONMENT variables.
See `Register` directory for all the **ENVIRONMENT** variables. `All of them` apply here as well. Create a file `APP_ENV` and source them before starting to build and publish the services.  

### Build and publish images to docker and services to IEAM exchange.

    make


