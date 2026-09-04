# Frack RBAC hardening

Frack keeps the read, log, metric, and Pod-restart access needed to operate the
business applications. It cannot use Kubernetes RBAC to read any Secret, exec
into any Pod, inspect sibling agent workloads, or mutate its own Deployment.

## Trust boundary

`frack-ops` lives in `agents-shared`, which also holds per-principal subagent
broker tokens. A namespace-wide Secret read would return token values, while
`pods/exec` or Deployment patch access could recover a token from a sibling
consumer even without Secret API access. The manifest therefore applies both
controls:

- The only `agents-shared` Role permits `get` on the named `frack` Deployment.
  It uses `resourceNames: [frack]` and has no mutation verb.
- Business namespace Roles permit observation, logs, and Pod deletion for a
  rolling restart. They do not permit `pods/exec` or Secret access.
- The cluster Role remains read-only and covers only Argo applications, nodes,
  namespaces, and resource metrics.

Mounted `frack-secrets` values are available to Frack's own process. Frack does
not need Secret API access to consume them. Human shell diagnostics use an
operator identity; they are not delegated to the autonomous agent.

## Offline verification

Run these checks against the exact revision proposed for deployment:

```bash
python3 homelab/scripts/test_rbac_policy.py
kubectl kustomize --load-restrictor=LoadRestrictionsNone homelab/k8s \
  >/private/tmp/frack-rendered.yaml
yq eval-all '.' /private/tmp/frack-rendered.yaml >/dev/null
git diff --check
```

The policy test resolves the Roles and bindings granted to
`agents-shared/frack-ops`. It proves named broker/client Secrets are denied,
Secret list/watch is absent, pod exec is denied in shared and business
namespaces, the shared namespace grant is resource-name scoped, and the intended
read/log/restart operations remain allowed.

## Commissioning order

Keep Frack and all autonomous workers paused throughout the RBAC change.

1. Merge and publish the reviewed Frack repository revision. Do not provision
   or rotate broker client tokens yet.
2. Sync only the Frack Argo application. Confirm the old `frack-self` Role and
   binding were pruned and the new `frack-self-observer` objects are reconciled.
3. As an operator, verify the live authorizer without reading Secret data:

   ```bash
   subject=system:serviceaccount:agents-shared:frack-ops
   kubectl auth can-i get secret/frick-subagent-client \
     -n agents-shared --as="$subject"                         # no
   kubectl auth can-i list secrets \
     -n agents-shared --as="$subject"                         # no
   kubectl auth can-i create pods/exec \
     -n agents-shared --as="$subject"                         # no
   kubectl auth can-i create pods/exec \
     -n blink-platform --as="$subject"                        # no
   kubectl auth can-i patch deployment/frack \
     -n agents-shared --as="$subject"                         # no
   kubectl auth can-i get deployment/frack \
     -n agents-shared --as="$subject"                         # yes
   kubectl auth can-i get pods/log \
     -n blink-platform --as="$subject"                        # yes
   kubectl auth can-i delete pods \
     -n blink-platform --as="$subject"                        # yes
   ```

4. Audit other service-account bindings that can read `agents-shared` Secrets
   or exec into broker credential consumers. Cluster administrators and the
   explicitly trusted Frick/Vimes operator boundary remain outside this patch.
5. Only after the negative authorization checks pass, provision one distinct
   broker token per approved principal. Mount only Frack's token into Frack.
6. Run the broker cross-principal acceptance test: Frack's token authenticates
   only as Frack and cannot authenticate as a sibling. Then commission one
   paused principal at a time under the global budget gate.

## Residual risk

Frack can still read Pod specifications and logs in business namespaces and can
delete their Pods. Business workloads must keep credentials out of inline Pod
environment values and logs. This patch does not reduce deliberate cluster-admin
or trusted Frick/Vimes access, and it does not itself prove broker deployment,
archive restore, per-principal attribution, or the 24-hour fleet soak. Those
remain activation gates.
