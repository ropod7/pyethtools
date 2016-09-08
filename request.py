# -*- coding: utf8 -*-
import sys
import pycurl, json
try:
    # Python 3
    from io import BytesIO
except ImportError:
    # Python 2
    from StringIO import StringIO as BytesIO

class EthConnectionError(Exception):
    def __init__(self, *args):
        super(EthConnectionError, self).__init__(
            "Failed to connect to %s port %s: Connection refused" % args
            )

class BaseRequest(object):
    def __init__(self, host, port):
        self._ipcaddr = "%s:%s" % (host, port)
        self._host = host
        self._port = port
        self._requestData = {"jsonrpc":"2.0","method":"","params":[],"id":0}

    def _executeCurl(self, postfields):
        self._buff = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(curl.URL, self._ipcaddr)
        # Content-Type header to application/json
        curl.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])
        # Sets request method to POST
        curl.setopt(curl.POST, 1)
        curl.setopt(curl.POSTFIELDS, postfields)
        curl.setopt(curl.WRITEDATA, self._buff)
        try:
            curl.perform()
        except pycurl.error:
            raise EthConnectionError(self._host, self._port)
        finally:
            curl.close()

    def _getRequestResult(self, requestData):
        decoder = json.JSONDecoder()
        postfields = json.dumps(requestData)
        self._executeCurl(postfields)
        body = self._buff.getvalue().decode('utf-8')
        self._buff.close()
        # Body is a string in some encoding.
        # In Python 2, we can print it without knowing what the encoding is.
        res = decoder.raw_decode(body)[0]
        return res

    def _setRequest(self, data):
        request = self._requestData.copy()
        request.update(data)
        try:
            return self._getRequestResult(request)['result']
        except KeyError:
            return "EthError: %s" % self._getRequestResult(request)['error']['message']

    def _setData(self, method, params=[], _id=1):
        return {"method": method, "params": params, "id": _id}

class PersonalRequest(BaseRequest):
    def personal_unlockAccount(self, address, password):
        """Given account to unlock. Returns True, or False.
        Parameters:
        1. DATA, 20 Bytes - The address of account.
        2. String, - account password"""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [address, password])
        return self._setRequest(data)

    def personal_lockAccount(self, address):
        """Lock given account. Returns True, or False.
        Parameters:
        1. DATA, 20 Bytes - The address of account."""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [address])
        return self._setRequest(data)

    def personal_newAccount(self, password):
        """Creates new account with given password and returns address.
        Parameters:
        1. String, - account password"""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [password])
        return self._setRequest(data)

class Request(BaseRequest):
    def web3_sha3(self, string):
        """Returns Keccak-256 (not the standardized SHA3-256) of the given data.
        Parameters:
        1. String - the data to convert into a SHA3 hash"""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [string], _id=64)
        return self._setRequest(data)

    @property
    def net_listening(self):
        "Returns true if client is actively listening for network connections."
        method = sys._getframe().f_code.co_name
        data = self._setData(method, _id=67)
        return self._setRequest(data)

    @property
    def net_peerCount(self):
        "Returns number of peers currenly connected to the client."
        method = sys._getframe().f_code.co_name
        data = self._setData(method, _id=74)
        return int(self._setRequest(data), 0)

    @property
    def eth_syncing(self):
        "Returns an object with data about the sync status or false."
        method = sys._getframe().f_code.co_name
        data = self._setData(method)
        result = self._setRequest(data)
        if result:
            bases = [0 for i in range(len(result))]
            return dict(zip(result.keys(), list(map(int, result.values(), bases))))
        return result

    @property
    def eth_coinbase(self):
        "Returns the client coinbase address."
        method = sys._getframe().f_code.co_name
        data = self._setData(method, _id=64)
        return self._setRequest(data)

    @property
    def eth_hashrate(self):
        "Returns the number of hashes per second that the node is mining with."
        method = sys._getframe().f_code.co_name
        data = self._setData(method, _id=71)
        return int(self._setRequest(data), 0)

    @property
    def eth_gasPrice(self):
        "Returns the current price per gas in wei."
        method = sys._getframe().f_code.co_name
        data = self._setData(method, _id=73)
        return int(self._setRequest(data), 0)

    @property
    def eth_accounts(self):
        "Returns a list of addresses owned by client."
        method = sys._getframe().f_code.co_name
        data = self._setData(method)
        return self._setRequest(data)

    @property
    def eth_blockNumber(self):
        "Returns the number of most recent block."
        method = sys._getframe().f_code.co_name
        data = self._setData(method, _id=83)
        return int(self._setRequest(data), 0)

    def eth_getBalance(self, address, block="latest"):
        """Returns the balance of the account of given address.
        Parameters:
        1. DATA, 20 Bytes - address to check for balance.
        2. QUANTITY|TAG - integer block number, or the string 'latest', 'earliest' or 'pending'"""
        block = hex(block) if isinstance(block, int) else block
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [address, block])
        return int(self._setRequest(data), 0)

    def eth_getStorageAt(self, address, pos, block="latest"):
        """Returns the value from a storage position at a given address.
        Parameters:
        1. DATA, 20 Bytes - address of the storage.
        2. QUANTITY - integer of the position in the storage.
        3. QUANTITY|TAG - integer block number, or the string 'latest', 'earliest' or 'pending'"""
        block = hex(block) if isinstance(block, int) else block
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [address, hex(pos), block])
        return self._setRequest(data)

    def eth_getTransactionCount(self, address, block="latest"):
        """Returns the number of transactions sent from an address.
        Parameters:
        1. DATA, 20 Bytes - address.
        2. QUANTITY|TAG - integer block number, or the string 'latest', 'earliest' or 'pending'"""
        block = hex(block) if isinstance(block, int) else block
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [address, block])
        return int(self._setRequest(data), 0)

    def eth_getBlockTransactionCountByHash(self, blockhash):
        """Returns the number of transactions in a block from a block matching the given block hash.
        Parameters:
        1. DATA, 32 Bytes - hash of a block"""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [blockhash])
        return self._setRequest(data)

    def eth_getBlockTransactionCountByNumber(self, block="latest"):
        """Returns the number of transactions in a block from a block matching the given block number.
        Parameters:
        1. QUANTITY|TAG - integer of a block number, or the string 'earliest', 'latest' or 'pending'"""
        block = hex(block) if isinstance(block, int) else block
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [block])
        return int(self._setRequest(data), 0)

    def eth_getUncleCountByBlockHash(self, blockhash):
        """Returns the number of uncles in a block from a block matching the given block hash.
        Parameters:
        1. DATA, 32 Bytes - hash of a block"""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [blockhash])
        return self._setRequest(data)

    def eth_getUncleCountByBlockNumber(self, block="latest"):
        """Returns the number of uncles in a block from a block matching the given block number.
        Parameters:
        1. QUANTITY|TAG - integer of a block number, or the string 'earliest', 'latest' or 'pending'"""
        block = hex(block) if isinstance(block, int) else block
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [block])
        return int(self._setRequest(data), 0)

    def eth_getCode(self, address, block="latest"):
        """Returns code at a given address.
        Parameters:
        1. DATA, 20 Bytes - address
        2. QUANTITY|TAG - integer block number, or the string 'latest', 'earliest' or 'pending'"""
        block = hex(block) if isinstance(block, int) else block
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [address, block])
        return self._setRequest(data)

    def eth_sign(self, address, sha3data):
        """Signs data with a given address.
        Note: the address to sign must be unlocked.
        Parameters:
        1. DATA, 20 Bytes - address
        2. DATA, 32 Bytes - sha3 hash of data to sign"""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [address, sha3data])
        return self._setRequest(data)

    def eth_sendTransaction(self, data):
        """Creates new message call transaction or a contract creation, if the data field contains code.
        Parameters:
        1. Object - The transaction object:
            - from: DATA, 20 Bytes - The address the transaction is send from.
            - to: DATA, 20 Bytes - (optional when creating new contract) The
            address the transaction is directed to.
            - gas: QUANTITY - (optional, default: 90000) Integer of the gas
            provided for the transaction execution. It will return unused gas.
            - gasPrice: QUANTITY - (optional, default: To-Be-Determined)
            Integer of the gasPrice used for each paid gas
            - value: QUANTITY - (optional) Integer of the value send with
            this transaction
            - data: DATA - The compiled code of a contract OR the hash of
            the invoked method signature and encoded parameters. For details see Ethereum Contract ABI
            - nonce: QUANTITY - (optional) Integer of a nonce. This allows
            to overwrite your own pending transactions that use the same nonce."""
        assert isinstance(data, dict), "Given Data must be a type of dict"
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [data])
        return self._setRequest(data)

    def eth_sendRawTransaction(self, data):
        """Creates new message call transaction or a contract creation for signed transactions.
        Parameters:
        1. DATA, The signed transaction data."""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [data])
        return self._setRequest(data)

    def eth_call(self, data, method=None, block="latest"):
        """Executes a new message call immediately without creating a transaction on the block chain.
        Parameters:
        1. Object - The transaction object:
            - from: DATA, 20 Bytes - The address the transaction is send from.
            - to: DATA, 20 Bytes - (optional when creating new contract) The
            address the transaction is directed to.
            - gas: QUANTITY - (optional, default: 90000) Integer of the gas
            provided for the transaction execution. It will return unused gas.
            - gasPrice: QUANTITY - (optional, default: To-Be-Determined)
            Integer of the gasPrice used for each paid gas
            - value: QUANTITY - (optional) Integer of the value send with
            this transaction
            - data: DATA - The compiled code of a contract OR the hash of
            the invoked method signature and encoded parameters. For details see Ethereum Contract ABI
            - nonce: QUANTITY - (optional) Integer of a nonce. This allows
            to overwrite your own pending transactions that use the same nonce.
        2. QUANTITY|TAG - integer block number, or the string 'latest', 'earliest' or 'pending'"""
        assert isinstance(data, dict), "Given Data must be a type of dict"
        method = sys._getframe().f_code.co_name if method is None else method
        data = self._setData(method, [data])
        if block is not None:
            block = hex(block) if isinstance(block, int) else block
            data['params'].append(block)
        return self._setRequest(data)

    def eth_estimateGas(self, data):
        """Makes a call or transaction, which won't be added to the blockchain
        and returns the used gas, which can be used for estimating the used gas.
        Parameters:
        See 'eth_call' parameters, expect that all properties are optional."""
        assert isinstance(data, dict), "Given Data must be a type of dict"
        method = sys._getframe().f_code.co_name
        return int(self.eth_call(data, method=method, block=None), 0)

    def eth_getBlockByHash(self, blockhash, fulltx=False):
        """Returns information about a block by hash.
        Parameters:
        1. DATA, 32 Bytes - Hash of a block.
        2. Boolean - If true it returns the full transaction objects,
        if false only the hashes of the transactions."""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [blockhash, fulltx])
        return self._setRequest(data)

    def eth_getBlockByNumber(self, block="latest", fulltx=False):
        """Returns information about a block by block number.
        Parameters:
        1. QUANTITY|TAG - integer of a block number, or the string 'earliest', 'latest' or 'pending'.
        2. Boolean - If true it returns the full transaction objects, if
        false only the hashes of the transactions."""
        block = hex(block) if isinstance(block, int) else block
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [block, fulltx])
        return self._setRequest(data)

    def eth_getTransactionByHash(self, txhash):
        """Returns the information about a transaction requested by transaction hash.
        Parameters:
        1. DATA, 32 Bytes - hash of a transaction"""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [txhash])
        return self._setRequest(data)

    def eth_getTransactionByBlockHashAndIndex(self, blockhash, index):
        """Returns information about a transaction by block hash and transaction index position.
        Parameters:
        1. DATA, 32 Bytes - hash of a block.
        2. QUANTITY - integer of the transaction index position."""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [blockhash, hex(index)])
        return self._setRequest(data)

    def eth_getTransactionByBlockNumberAndIndex(self, index, block="latest"):
        """Returns information about a transaction by block number and transaction index position.
        Parameters:
        1. QUANTITY|TAG - a block number, or the string 'earliest', 'latest' or 'pending'.
        2. QUANTITY - the transaction index position."""
        block = hex(block) if isinstance(block, int) else block
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [block, hex(index)])
        return self._setRequest(data)

    def eth_getTransactionReceipt(self, txhash):
        """Returns the receipt of a transaction by transaction hash.
        Note: That the receipt is not available for pending transactions.
        Parameters:
        1. DATA, 32 Bytes - hash of a transaction"""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [txhash])
        return self._setRequest(data)

    def eth_getUncleByBlockHashAndIndex(self, blockhash, index):
        """Returns information about a uncle of a block by hash and uncle index position.
        Parameters:
        1. DATA, 32 Bytes - hash a block.
        2. QUANTITY - the uncle's index position."""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [blockhash, hex(index)])
        return self._setRequest(data)

    def eth_getUncleByBlockNumberAndIndex(self, index, block="latest"):
        """Returns information about a uncle of a block by number and uncle index position.
        Parameters:
        1. QUANTITY|TAG - a block number, or the string 'earliest', 'latest' or 'pending'.
        2. QUANTITY - the uncle's index position."""
        block = hex(block) if isinstance(block, int) else block
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [block, hex(index)])
        return self._setRequest(data)

    def eth_compileSolidity(self, code):
        """Returns compiled solidity code.
        Parameters:
        1. String - The source code."""
        assert isinstance(code, str), "Code to compile must be an string."
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [code])
        return self._setRequest(data)

    def eth_newFilter(self, data, method=None, _id=73):
        """Creates a filter object, based on filter options, to notify when
        the state changes (logs). To check if the state has changed, call 'eth_getFilterChanges'.
        A note on specifying topic filters:
        Topics are order-dependent. A transaction with a log with topics [A, B]
        will be matched by the following topic filters:
        - [] "anything"
        - [A] "A in first position (and anything after)"
        - [null, B] "anything in first position AND B in second position (and anything after)"
        - [A, B] "A in first position AND B in second position (and anything after)"
        - [[A, B], [A, B]] "(A OR B) in first position AND (A OR B) in second position (and anything after)"
        Parameters:
        1. Object - The filter options:
            - fromBlock: QUANTITY|TAG - (optional, default: 'latest') Integer
            block number, or "latest" for the last mined block or 'pending', 'earliest'
            for not yet mined transactions.
            - toBlock: QUANTITY|TAG - (optional, default: 'latest') Integer block number,
            or 'latest'for the last mined block or 'pending', 'earliest' for not yet
            mined transactions.
            - address: DATA|Array, 20 Bytes - (optional) Contract address or a list of
            addresses from which logs should originate.
            - topics: Array of DATA, - (optional) Array of 32 Bytes DATA topics. Topics
            are order-dependent. Each topic can also be an array of DATA with 'or' options."""
        assert isinstance(data, dict), "Given Data must be a type of dict"
        if method is None:
            method = sys._getframe().f_code.co_name
        data = self._setData(method, [data], _id=_id)
        return self._setRequest(data)

    @property
    def eth_newBlockFilter(self):
        """Creates a filter in the node, to notify when a new block arrives.
        To check if the state has changed, call 'eth_getFilterChanges'."""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, _id=73)
        return self._setRequest(data)

    @property
    def eth_newPendingTransactionFilter(self):
        """Creates a filter in the node, to notify when new pending transactions arrive.
        To check if the state has changed, call 'eth_getFilterChanges'."""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, _id=73)
        return self._setRequest(data)

    def eth_uninstallFilter(self, filterId):
        """Uninstalls a filter with given id. Should always be called when watch
        is no longer needed. Additonally Filters timeout when they aren't
        requested with 'eth_getFilterChanges' for a period of time.
        Parameters:
        1. QUANTITY - The filter id."""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [filterId], _id=73)
        return self._setRequest(data)

    def eth_getFilterChanges(self, filterId):
        """Polling method for a filter, which returns an array of logs which
        occurred since last poll.
        Parameters:
        1. QUANTITY - the filter id."""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [filterId], _id=73)
        return self._setRequest(data)

    def eth_getFilterLogs(self, filterId):
        """Returns an array of all logs matching filter with given id.
        Parameters:
        1. QUANTITY - The filter id."""
        method = sys._getframe().f_code.co_name
        data = self._setData(method, [filterId], _id=73)
        return self._setRequest(data)

    def eth_getLogs(self, data):
        """Returns an array of all logs matching a given filter object.
        Parameters:
        1. Object - the filter object, see 'eth_newFilter' parameters."""
        method = sys._getframe().f_code.co_name
        return self.eth_newFilter(data, method=method, _id=74)

    @property
    def eth_getWork(self):
        """Returns the hash of the current block, the seedHash, and the boundary
        condition to be met ("target").
        Returns:
        Array - Array with the following properties:
            1. DATA, 32 Bytes - current block header pow-hash
            2. DATA, 32 Bytes - the seed hash used for the DAG.
            3. DATA, 32 Bytes - the boundary condition ("target"), 2^256 / difficulty."""
        method = sys._getframe().f_code.co_name
        data = self._setData(method)
        return self._setRequest(data)
