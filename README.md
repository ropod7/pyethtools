# pyethtools
1. Contains Ethereum JSON-RPC cover in request.py module.
2. Hex encode tools for encode additional parameters using transactions.
# Usage
.. code-block::
  from pyethtools.request import PersonalRequest, Request
  from pyethtools import hextools as ht

  _ipcaddr = 'http://localhost', 8545
  r = Request(*_ipcaddr)
  pr = PersonalRequest(*_ipcaddr)

  coinbase = r.eth_coinbase
  account = pr.personal_newAccount("password") # returns accounts private address

  unlocked = pr.personal_unlockAccount(account, "password") # returns True or False

  # To encode additional parameters:
  method = "testCall(uint,uint32[],bytes10,string)"
  contractAddress = "0x981118d6a516707f2ece6fd50d0000414dc014ac"

  # following two method calls are equal in Geth JavaScript Console 'web3.sha3(method)':
  hexstr = ht.strToHex(method) # 0x7465737443616c6c2875696e742c75696e7433325b5d2c627974657331302c737472696e6729
  signature = r.web3_sha3(method) # 0x96081302811f55aff14451d09c81b2a499b71fd6387d5480bb6b5afa56f0e663

  txData = ht.getMethodID(signature) # 0x96081302 is methodID

  # make transaction:
  if unlocked:
    data = {
	"from" : account,
	"to"   : contractAddress,
	"gas"  : 10**6,
	"data" : ht.getData([2**16, ['0x972', 123], "0123456789", "Hello, world!"], data=txData)  # encoding additional data
	# ht.getData returns:
	# 0x96081302
	# 0000000000000000000000000000000000000000000000000000000000010000
	# 0000000000000000000000000000000000000000000000000000000000000080
	# 3031323334353637383900000000000000000000000000000000000000000000
	# 00000000000000000000000000000000000000000000000000000000000000e0
	# 0000000000000000000000000000000000000000000000000000000000000002
	# 0000000000000000000000000000000000000000000000000000000000000972
	# 000000000000000000000000000000000000000000000000000000000000007b
	# 000000000000000000000000000000000000000000000000000000000000000d
	# 48656c6c6f2c20776f726c642100000000000000000000000000000000000000
    	}

	estimateGas = r.eth_estimateGas(data)
	txcost = estimateGas * r.eth_gasPrice
	if r.eth_getBalance(account) > txcost:
	tx = r.eth_sendTransaction(data)
	pr.personal_lockAccount(account)
	print tx # returns transaction hash


