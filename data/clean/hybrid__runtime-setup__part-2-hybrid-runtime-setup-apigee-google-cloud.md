---
title: "Part 2: Hybrid runtime setup  |  Apigee  |  Google Cloud"
product: Hybrid
topic: runtime_setup
url: https://cloud.google.com/apigee/docs/hybrid/v1.9/install-before-begin?hl=en
fetched_at: 1760059517
---

Installation of hotfixes
Supported platforms
You can install Apigee hybrid on a number of platforms, including Anthos on premises, AWS, Bare Metal, EKS, Google Kubernetes Engine (GKE), OpenShift, and others. For a list of supported platforms see Apigee hybrid: supported platforms.
Permissions
Each supported platform has its own permission requirements for creating a cluster. As cluster owner, you can proceed to install the Apigee-specific components (including cert-manager and the Apigee runtime) into the cluster. However, if you want to delegate to another user the installation of the runtime components into the cluster, you can manage the necessary permissions through Kubernetes authn-authz.
For a complete list of Kubernetes resources and custom resources that are used by Apigee installations, see Kubernetes and custom resources used by Apigee.
Prerequisites
This section describes tasks you must accomplish before you begin the runtime plane quickstart install.
| Complete the tasks in Part 1: Project and org setup before you begin the runtime installation: |
|---|
|
|
|
|
|
|
|
|
| Next step: Create a cluster |
