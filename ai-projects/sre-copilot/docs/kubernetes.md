# CrashLoopBackOff

CrashLoopBackOff occurs when a container repeatedly crashes.

Troubleshooting:

1. kubectl describe pod
2. kubectl logs
3. Check image version
4. Verify probes

# ImagePullBackOff

Occurs when image cannot be downloaded.

Troubleshooting:

1. Verify image name
2. Verify registry credentials
3. Check network access
