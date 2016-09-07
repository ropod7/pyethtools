=================================
pyEthTools: Python Ethereum Tools
=================================

1. Contains Ethereum JSON-RPC cover.
2. Hexnumber encode tools for encode additional parameters in transactions.
3. Hexnumber decode tools for decode data that contract returns.

Example of usage:
----------------------------------

.. code-block:: python

    from pyethtools import PersonalRequest, Request
    from pyethtools import hextools as ht

    _ipcaddr = 'http://localhost', 8545
    r = Request(*_ipcaddr)
    pr = PersonalRequest(*_ipcaddr)

    coinbase = r.eth_coinbase
    account = pr.personal_newAccount("password") # returns accounts private address
    contractAddress = "0x123" # as example

    # To encode additional parameters:
    method = "testCall(uint,uint32[],bytes10,string)"
    # following two method calls are equal in 'web3.sha3(method)':
    hexstr = ht.toHex(method)
    print hexstr
    # 0x7465737443616c6c2875696e742c75696e7433325b5d2c627974657331302c737472696e6729
    signature = r.web3_sha3(method)
    print signature
    # 0x96081302811f55aff14451d09c81b2a499b71fd6387d5480bb6b5afa56f0e663
    txData = ht.getMethodID(signature) # 0x96081302 is methodID

    unlocked = pr.personal_unlockAccount(account, "password") # returns True or False

    # make transaction:
    if unlocked:
        data = {
            "from" : account,
            "to"   : contractAddress,
            "gas"  : 10**6,
            # NB: On giving a list of parameters make shore that the additional
            # sequence of list is equals to a contract constructor or function
            # call arguments for the required encoding, because 'getData' is not
            # a compiler.
            # Example of given function "testCall(uint,uint32[],bytes10,string)":
            "data" : ht.getData(
                    [2**16, ['0x972', 123], "0123456789", "Hello, world!"],
                    data=txData
                    ),

            # getData returns:
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
        else:
            print "balance is too low"

Let's imagine that function returns single Hexnumber of:
    (uint8, address, bytes10, string, uint[3], string)

.. code-block:: shell

    0x
    00000000000000000000000000000000000000000000000000000000000000ff
    000000000000000000000000ca35b7d915458ef5401234568dfe2f44e8fa733c
    3132333435363738390000000000000000000000000000000000000000000000
    0000000000000000000000000000000000000000000000000000000000000100
    0000000000000000000000000000000100000000000000000000000000000000
    0000000000000000000000000000000000000000000000000000000000000221
    0000000000000000000000000000000000000000000000000000000000000000
    0000000000000000000000000000000000000000000000000000000000000140
    0000000000000000000000000000000000000000000000000000000000000008
    d0b7d0b0d0b7d0b0000000000000000000000000000000000000000000000000
    0000000000000000000000000000000000000000000000000000000000000221
    54686520536f6c6964697479206f7074696d697a6572206f7065726174657320
    6f6e20617373656d626c792c20736f2069742063616e20626520616e6420616c
    736f2069732075736564206279206f74686572206c616e6775616765732e2049
    742073706c697473207468652073657175656e6365206f6620696e7374727563
    74696f6e7320696e746f20626173696320626c6f636b73206174204a554d5073
    20616e64204a554d5044455354732e20496e7369646520746865736520626c6f
    636b732c2074686520696e737472756374696f6e732061726520616e616c7973
    656420616e64206576657279206d6f64696669636174696f6e20746f20746865
    20737461636b2c20746f206d656d6f7279206f722073746f7261676520697320
    7265636f7264656420617320616e2065787072657373696f6e20776869636820
    636f6e7369737473206f6620616e20696e737472756374696f6e20616e642061
    206c697374206f6620617267756d656e74732077686963682061726520657373
    656e7469616c6c7920706f696e7465727320746f206f74686572206578707265
    7373696f6e732e20546865206d61696e2069646561206973206e6f7720746f20
    66696e642065787072657373696f6e7320746861742061726520616c77617973
    20657175616c20286f6e20657665727920696e7075742920616e6420636f6d62
    696e65207468656d20696e746f20616e2065787072657373696f6e20636c6173
    7300000000000000000000000000000000000000000000000000000000000000

Example of decode:
----------------------

.. code-block:: python

    hx = ht.toHex("readData()")
    methodID = ht.getMethodID(r.web3_sha3(hx))
    data = {
        "from" : coinbase,
        "to"   : contractAddress,
        "data" : methodID,
    }
    methodData = r.eth_call(data)

    # Now we will decode received methodData:
    for l in ht.decodeData(methodData):
        print l

    # So, the decoded data should looks like:
    # 255
    # 0xca35b7d915458ef5401234568dfe2f44e8fa733c
    # 123456789
    # 340282366920938463463374607431768211456
    # 545
    # 0
    # заза
    # The Solidity optimizer operates on assembly, so it can be and also is
    # used by other languages. It splits the sequence of instructions into
    # basic blocks at JUMPs and JUMPDESTs. Inside these blocks, the instructions
    # are analysed and every modification to the stack, to memory or storage is
    # recorded as an expression which consists of an instruction and a list of
    # arguments which are essentially pointers to other expressions. The main
    # idea is now to find expressions that are always equal (on every input) and
    # combine them into an expression class

    # for more complex data we may use the 'decodeArgData':
    for l in ht.decodeArgData(methodData, types=(int, hex, str, str, [int, int, int], str)):
        print l

    # 255
    # 0xca35b7d915458ef5401234568dfe2f44e8fa733c
    # 123456789
    # [340282366920938463463374607431768211456L, 545, 0]
    # заза
    # The Solidity optimizer operates on assembly, so it can be and also is
    # used by other languages. It splits the sequence of instructions into
    # basic blocks at JUMPs and JUMPDESTs. Inside these blocks, the instructions
    # are analysed and every modification to the stack, to memory or storage is
    # recorded as an expression which consists of an instruction and a list of
    # arguments which are essentially pointers to other expressions. The main
    # idea is now to find expressions that are always equal (on every input) and
    # combine them into an expression class
