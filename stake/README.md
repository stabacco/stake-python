Stake
======
**Stake** is an unofficial and opinionated Python client for the [Stake](https://www.stake.com.au) trading platform.

This library wraps the current Stake RPC api and allows common trade operations, such as submitting buy/sell requests, checking your portfolio etc...

Please note that, at the current stage, the Stake client is asynchronous.


## Download
* [Version X.Y](https://github.com/username/sw-name/archive/master.zip)
* Other Versions

## Usage
```$
pip install stake-python
```

## Quickstart

After you install the package, you will need to authenticate to Stake in order to get authorization to interact with your account. Stake will respond with a session token which will need to be send in the header for all the requests needing authentication.

You can either login with your username/password

```python
import asyncio
import os
import stake

 login_request = stake.CredentialsLoginRequest(username=os.environ["STAKE_USER"], password=os.environ["STAKE_PASS"])

client = asyncio.run(stake.StakeClient(login_request))

```

## Contributors

### Contributors on GitHub
* [Contributors](https://github.com/username/sw-name/graphs/contributors)


### Third party libraries
* see [LIBRARIES](https://github.com/username/sw-name/blob/master/LIBRARIES.md) files

## License
* see [LICENSE](https://github.com/username/sw-name/blob/master/LICENSE.md) file

## Version
* Version X.Y

## How-to use this code
* see [INSTRUCTIONS](https://github.com/username/sw-name/blob/master/INSTRUCTIONS.md) file

## Contact
#### Developer/Company
* Homepage:
* e-mail:
* Twitter: [@twitterhandle](https://twitter.com/twitterhandle "twitterhandle on twitter")
* other communication/social media

[![Flattr this git repo](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=username&url=https://github.com/username/sw-name&title=sw-name&language=&tags=github&category=software)
