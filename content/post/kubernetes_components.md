---
title: "Kubernetes components"
date: 2023-04-03T12:33:21-06:00
Description: "This is a brief description of the components that make up a Kubernetes cluster"
Tags: ["kubernetes", "components"]
Thumbnail: "images/kubernetes-logo.png"
Categories: ["kubernetes"]
DisableComments: false
---

Hello reader, Jorge here. I'll be starting a series of articles about Kubernetes since I'm studying for the [CKAD exam](https://training.linuxfoundation.org/full-catalog/?_sft_product_type=certification&sscid=).

In this post I will be talking about the components that make up a Kubernetes cluster. I will be using the following diagram to explain the building blocks:

![Kubernetes Components](/images/components-of-kubernetes.png)

The diagram above shows the components that make up a Kubernetes cluster. The components are divided into two groups:

- The control plane: Manages the worker nodes and the Pods in the cluster. Additionally, it makes components make global decisions about the cluster (for example, scheduling), as well as detecting and responding to cluster events (for example, starting up a new pod when a deployment's `replicas` field is unsatisfied).
- The worker nodes: The actual machines running your contasinerized applications (for example, Pods). The worker nodes may be VMs or physical machines, depending on your cluster. Each node has the services necessary to run Pods and is managed by the control plane.

As we see on the previous diagram, we can see that the control plane is made up of the following components:

- **etcd**: A distributed key-value store that stores all the data used to manage the cluster.
- **kube-apiserver**: The component that exposes the Kubernetes API. It is the front-end for the Kubernetes control plane.
- **kube-controller-manager**: A control loop that watches the state of your cluster and makes changes to move the current state towards the desired state.
- **kube-scheduler**: The component that schedules Pods to Nodes.

The worker nodes are made up of the following components:

- **kubelet**: An agent that runs on each node in the cluster. It makes sure that containers are running in a Pod.
- **kube-proxy**: A network proxy that runs on each node in your cluster, implementing part of the Kubernetes Service concept.
- **container runtime**: The software that is responsible for running containers.

In a traditional cluster, we would have a single master node and multiple worker nodes. However, in a highly available cluster, we would have multiple master nodes and multiple worker nodes.

In a managed environment like AKS, GKE, EKS, etc. we don't have to worry about the control plane since it is managed by the cloud provider. However, in a self-managed environment, we would have to manage the control plane ourselves, and have procedures in place to ensure that the control plane is highly available, the data is backed up, etc.


**Source**: [Kubernetes Components](https://kubernetes.io/docs/concepts/overview/components/)