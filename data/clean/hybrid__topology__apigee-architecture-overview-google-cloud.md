---
title: "Apigee architecture overview  |  Google Cloud"
product: Hybrid
topic: topology
url: https://cloud.google.com/apigee/docs/api-platform/architecture/overview?hl=en
fetched_at: 1760059514
---

This page applies to Apigee and Apigee hybrid.
View Apigee Edge documentation.
This topic provides an overview of the Apigee system architecture. It is intended to help you understand which components are created during provisioning and their purpose in the overall system.
Apigee provides two options for provisioning: with VPC peering and without VPC peering. Both options are described in the sections that follow.
Architecture with VPC peering enabled
This section describes the Apigee system architecture when Apigee is provisioned with the VPC peering option.
Provisioning overview
During provisioning, components are configured and created that allow bidirectional communication between a virtual private cloud network (VPC) managed by you and a VPC network managed by Apigee. After you complete the first few provisioning steps, the two VPCs exist, but as yet cannot communicate back and forth. Further configuration is needed to allow bidirectional communication. See Figure 1.
To enable communication between VPCs, we use VPC network peering. Network peering allows internal IP address connectivity across two Virtual Private Cloud (VPC) networks regardless of whether they belong to the same project or the same Google Cloud organization. After the network peering step is completed, communication is possible between the two VPCs. See Figure 2.
To route traffic from client apps on the internet to Apigee, we use a global external HTTPS load balancer (XLB). An XLB can communicate across Google Cloud projects, such as between the customer Google Cloud project and the Apigee Google Cloud Project, using cross-project service referencing.
You could also provision a managed instance group (MIG) of virtual machines (VM) that serve as a network bridge. The MIG VMs have the capability to communicate bidirectionally across the peered networks. When provisioning is complete, apps on the internet talk to the XLB, the XLB talks to the bridge VM, and the bridge VM talks to the Apigee network. See Figure 3 and Figure 4.
In this configuration, traffic is routed from Apigee (for example, from the MessageLogging policy) to a workload running in your internal VPC. In this case, communication to your internal VPC does not go through a NAT IP of the Egress. Instead, you can route the traffic through one of the Apigee instance IPs.
API proxy call lifecycle
The following illustration shows the lifecycle of an API proxy call as it moves through the provisioned Apigee system components (Figure 5):
- A client app calls an Apigee API proxy.
- The request lands on a global L7 external HTTPS load balancer (XLB). The XLB is configured with an external/public IP and a TLS certificate.
- The XLB sends the request to a virtual machine (VM). The VM serves as a bridge between your VPC and Google's VPC (managed by Apigee).
- The VM sends the request to Apigee, which processes the API proxy request.
- Apigee sends the request to the backend service, and the response is sent back to the client.
Architecture with VPC peering disabled
This section describes the Apigee system architecture when Apigee is not provisioned with the VPC peering option.
During provisioning, components are configured and created that allow bidirectional communication between a virtual private cloud network (VPC) managed by you and a VPC network managed by Apigee. After you complete the first few provisioning steps, the two VPCs exist, but as yet cannot communicate back and forth. Further configuration is needed to allow bidirectional communication. See Figure 6.
To enable communication between VPCs, we use Private Service Connect (PSC) for routing northbound traffic to Apigee and southbound traffic to target services running in your Google Cloud projects.
PSC enables private connection between a service producer (Apigee) and a service consumer (one or more other Cloud projects that you control). With this method (Figure 7), requests pass through either a global external load balancer or a regional external load balancer to a single point of attachment, called a service attachment.
To privately connect Apigee to a backend target, you must create two entities: a service attachment in the VPC network where the target is deployed and an endpoint attachment in the Apigee VPC. These two entities allow Apigee to connect to the target service. See Southbound networking patterns.
The steps for provisioning Apigee with PSC (without VPC peering) are described in Command line provisioning without VPC peering.
