# ACME Project: Frequently Asked Questions

## I get incomplete points for the `invalid-certificate` test although my implementation seems to behave correctly.

Your DNS server should not be reachable (or at least not respond with the right records) after the invalid certificate has been detected by your client. 
It is desired that your HTTPS server is not reachable, because you cannot start it anyway if you have not obtained a certificate.

## My implementation works locally, but not in the GitLab CI. Specifically, my servers do not seem to receive anything.

You probably bound your servers to the `localhost` interface (IP address `127.0.0.1`) instead of the IP provided via the `record` argument (or IP address `0.0.0.0`).
While this configuration works fine for local testing, it will not work in the GitLab environment, where requests will be received from different machines.

## I use `flask` in Python and my HTTP challenge server does not seem to be accessible. Why is that?

In the past few years, we encountered this issue when running the Flask server in a separate process, and could solve it when running the Flask server in a thread of the main process instead.

## I just cannot get my JWS to work correctly.

Some pitfalls to avoid when creating the JWS:

- Don't use the default base64 encoding, but the url-safe base4 encoding with trailing '=' removed (as per [Section 2 of RFC 7515](https://www.rfc-editor.org/rfc/rfc7515#section-2)).
- Remove whitespace and line-breaks in the json dump that should be encoded (ibid).
- Use a proper byte encoding of the integer key parameters (e and n in RSA): The resulting byte string of an integer i should be ceil( i.bit_length() / 8 ) bytes long
- Create the signature with PKCSv1.5 padding and the SHA256 hash function (as in [Appendix A.2 of RFC7515](https://www.rfc-editor.org/rfc/rfc7515#appendix-A.2)) 

## My implementation passes the DNS challenges by the ACME server, but not the DNS tests after the protocol run.

When the ACME protocol run finishes, the testing setup tests your DNS server once again. In this test, the `dns.resolver` from `dnspython` is used, which we have learned to be a lot less forgiving than other DNS client implementations (e.g., the one used by ACME, which accepts your DNS response). The hint to the used library should help you in debugging.

## The scores of my implementation vary from run to run.

 We have made the experience that students who use `socketserver` and `BaseRequestHandler` for the DNS server get unstable results. This issue can be remedied by using `dnslib.DNSServer` instead.

 ## The test setup seems to not find my `run` script.

Confusingly, the problem is not that `/project/run` does not exist (it does), but that the first line of `project/run` reads to a Unix system as `#!/bin/bash^M` instead of `#!/bin/bash` (if the file was edited under Windows). 
It is the interpreter `/bin/bash^M` that does not exist. The `^M` is a carriage return added by DOS. You can fix the format of your `project/run` file as described [here](http://www.nazmulhuda.info/-bin-bash-m-bad-interpreter-no-such-file-or-directory).

## I have trouble installing Pebble.

If you run into the error `installing executables with 'go get' in module mode is deprecated`, the following worked in recent years:

- install go
- setup the gopath (to `/usr/local/go/bin`)
- run `go install github.com/letsencrypt/pebble/...@latest`
- `cd go/bin`
- You now should see the pebble executable. For some reason though go doesn't want to add the config
- manually download the pebble files from the github and add them all to `go/bin`