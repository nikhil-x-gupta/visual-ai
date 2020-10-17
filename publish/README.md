#### Source code for containers, services, policies and corresponding defintion files.

#### Build, Publish and Use in a shared IEAM environment

Using a shared single tenant instance creates several challenges when services, patterns and policies need to be published in a common exchange under one org structure without multiple developers clobbering over each other.

#### Issues

- Developers need to identify their service, pattern and policies among many similar assets (concept of owner)
- Developers may have project for demo, dev, test and more ( group the assets)
- Developers need to use their own docker repository (specify own docker account)

The tooling outlined below addresses these concerns and builds on top of existing infrastructure

### Automated Steps

Start with reviewing Makefile for targets.

Build and publish images to docker and services to exchange. Can be executed again and again.

    make


