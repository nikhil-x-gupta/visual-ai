### Development of containers, services, policies and defintion files

#### Using a shared IEAM environment to Build and Publish serrvices 

Using a shared instance creates some challenges when services, patterns and policies need to be published in a common exchange under one org without multiple developers clobbering over each other. 

#### Issues

- Developers need to identify their service, pattern and policies among many similar assets (concept of owner)
- Developers may have project for demo, dev, test and more ( group the assets)
- Developers need to use their own docker repository (specify own docker account)

The tooling outlined here addresses these issues and builds all the container images as per the specified target.

#### Automated Steps

Start with reviewing Makefile for targets.

#### `MUST` Setup ENVIRONMENT variables.
See `Register` directory for all the **ENVIRONMENT** variables. `All of them` apply here as well. Create a file `APP_ENV` and source them before starting to build and publish the services.  

#### Build and publish images to docker and services to IEAM exchange.
Suggest to start with `TensorFlow lite`. Review `Makefile` for the build targets.

- TensorFlow lite
```
make tflite-all
```
- PyTorch
```
make pth-all
```
- OpenVINO
```
make vino-all
```
- MVI
```
mvi-all
```

- Build for all frameworks
```
make
```

