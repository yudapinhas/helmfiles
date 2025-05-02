# Toolset 

## Helmfile

https://github.com/roboll/helmfile/releases

## Helm Plugins

### Helm Diff
```
helm plugin install https://github.com/databus23/helm-diff
```

# Usage

## The Helmfile Best Practices Guide
https://github.com/roboll/helmfile/blob/master/docs/writing-helmfile.md

## Apply

### All releases

```
helmfile -e eks-lab-cluster apply --args force
```
Where eks-lab-cluster environement configured in environments.yaml file.

### Single release

```
helmfile -e eks-lab-cluster -l name=cluster-autoscaler apply
```
Where "name=cluster-autoscaler" is release name.

## Debug

```
helmfile --log-level debug -e eks-lab-cluster apply
```

# Migration from Helm2 to Helm3

# Dependencies

## Install Helm v3

1. Download and extract latest release from this link: https://github.com/helm/helm/releases
2. Run the following:

```
mv linux-amd64/helm /usr/local/bin/helm3
```

## Configure helm v3

```
export XDG_CONFIG_HOME=$HOME/.helm3/config
export XDG_CACHE_HOME=$HOME/.helm3/cache
export XDG_DATA_HOME=$HOME/.helm3/share
helm3 plugin install https://github.com/helm/helm-2to3
helm3 plugin install https://github.com/databus23/helm-diff --version v3.0.0-rc.7
```

## Migrate releases to helm v3

```
export HELM_V3_CONFIG=$XDG_CONFIG_HOME
export HELM_V3_DATA=$XDG_DATA_HOME
helm3 2to3 move config
helm list -q| while read i; do helm3 2to3 convert $i ;done
helm3 list --all-namespaces
```

## Delete helm v2 from cluster

```
helm3 2to3 cleanup
```

## Run helmfile

helmfile must be executed with '-b' parameter. Example:

```
helmfile -b /usr/local/bin/helm3 -e eks-lab-cluster -l name=cluster-autoscaler apply
```
Note: Jenkins library for the pipeline must be updated accordingly.

