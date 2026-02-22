# generate certs

## macOS example

Install utils

```shell
brew install mkcert nss
```

Generate certs

```shell
mkcert -cert-file local-cert.pem -key-file local-key.pem "banking.test" "attacker.test" "localhost" "127.0.0.1"
```

Install certs

```shell
mkcert -install
```
