from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import json
from datetime import datetime

rpc_user = 'quaker_quorum'
rpc_password = 'franklin_fought_for_continental_cash'
rpc_ip = '3.134.159.30'
rpc_port = '8332'

rpc_connection = AuthServiceProxy(
    "http://%s:%s@%s:%s" % (rpc_user, rpc_password, rpc_ip, rpc_port))

###################################


class TXO:
    def __init__(self, tx_hash, n, amount, owner, time):
        # tx_hash - (string) the tx_hash on the Bitcoin blockchain
        self.tx_hash = tx_hash
        # n - (int) the position of this output in the transaction
        self.n = n
        # amount - (int) the value of this transaction output (in Satoshi)
        self.amount = amount
        # owner - (string) the Bitcoin address of the owner of this output
        self.owner = owner
        # time - (Datetime) the time of this transaction as a datetime object
        self.time = time
        # inputs - (TXO[]) a list of TXO objects
        self.inputs = []

    def __str__(self, level=0):
        ret = "\t"*level+repr(self.tx_hash)+"\n"
        for tx in self.inputs:
            ret += tx.__str__(level+1)
        return ret

    def to_json(self):
        fields = ['tx_hash', 'n', 'amount', 'owner']
        json_dict = {field: self.__dict__[field] for field in fields}
        json_dict.update({'time': datetime.timestamp(self.time)})
        if len(self.inputs) > 0:
            for txo in self.inputs:
                json_dict.update({'inputs': json.loads(txo.to_json())})
        return json.dumps(json_dict, sort_keys=True, indent=4)

    # this classmethod should connect to the Bitcoin blockchain,
    # and retrieve the nth output of the transaction with the given hash. Then it should create a new object
    @classmethod
    def from_tx_hash(cls, tx_hash, n=0):

        # YOUR CODE HERE
        try:
            # The function, getrawtransaction, connects to our Bitcoin node,
            # and returns a Python dict containing all the information about the transaction specified by tx_hash.
            tx = rpc_connection.getrawtransaction(tx_hash, True)
        except IndexError:
            print("No such hash")

        for tx_output in tx["vout"]:
            if tx_output["n"] == n:
                txo_obj = TXO(tx_hash=tx["hash"], n=tx_output["n"], amount=float(tx_output["value"])* pow(10, 8),
                              owner=tx_output["scriptPubKey"]["addresses"][0], time=datetime.fromtimestamp(tx["time"]))
        return txo_obj

    # this method should connect to the Bitcoin blockchain, and populate the list of inputs, up to a depth d.
    # In other words, if d=1 it should create TXO objects to populate self.inputs with the appropriate TXO objects.
    # If d=2 it should also populate the inputs field of each of the TXOs in self.inputs etc.
    def get_inputs(self, d=1):
        
    # -use the list of inputs on the TXO object calling get_inputs to retrieve the list of (2) input tx hashes
    # -use the from_tx_hash function to get the TXO object for each of these these tx hashes and append them to the self.inputs - this satisfies d=1
    # -then you would need to call get_inputs on the two inputs for d=1 -- this satisfies d=2
        
        d = d -1
        # YOUR CODE HERE
        # TXO.append_input_blocks(self, self.tx_hash)
        tx = rpc_connection.getrawtransaction(self.tx_hash, True)
        
        # loop over the list of transaction inputs
        for tx_input in tx["vin"]:
            # getting the block of each input 
            previous_txid = rpc_connection.getrawtransaction(tx_input["txid"], True)
            # generate TXO obj of each input transection
            generated_block = TXO.from_tx_hash(previous_txid["txid"])
            # append back
            self.inputs.append(generated_block)

        # print(self.inputs)

        if (d>0):
            for item in self.inputs:
                TXO.get_inputs(item, d)

        return



# Result (if verbose is set to true):
# {
#   "in_active_chain": b, (bool) Whether specified block is in the active chain or not (only present with explicit "blockhash" argument)
#   "hex" : "data",       (string) The serialized, hex-encoded data for 'txid'
#   "txid" : "id",        (string) The transaction id (same as provided)
#   "hash" : "id",        (string) The transaction hash (differs from txid for witness transactions)
#   "size" : n,             (numeric) The serialized transaction size
#   "vsize" : n,            (numeric) The virtual transaction size (differs from size for witness transactions)
#   "weight" : n,           (numeric) The transaction's weight (between vsize*4-3 and vsize*4)
#   "version" : n,          (numeric) The version
#   "locktime" : ttt,       (numeric) The lock time
#   "vin" : [               (array of json objects)
#      {
#        "txid": "id",    (string) The transaction id
#        "vout": n,         (numeric)
#        "scriptSig": {     (json object) The script
#          "asm": "asm",  (string) asm
#          "hex": "hex"   (string) hex
#        },
#        "sequence": n      (numeric) The script sequence number
#        "txinwitness": ["hex", ...] (array of string) hex-encoded witness data (if any)
#      }
#      ,...
#   ],
#   "vout" : [              (array of json objects)
#      {
#        "value" : x.xxx,            (numeric) The value in BTC
#        "n" : n,                    (numeric) index
#        "scriptPubKey" : {          (json object)
#          "asm" : "asm",          (string) the asm
#          "hex" : "hex",          (string) the hex
#          "reqSigs" : n,            (numeric) The required sigs
#          "type" : "pubkeyhash",  (string) The type, eg 'pubkeyhash'
#          "addresses" : [           (json array of string)
#            "address"        (string) bitcoin address
#            ,...
#          ]
#        }
#      }
#      ,...
#   ],
#   "blockhash" : "hash",   (string) the block hash
#   "confirmations" : n,      (numeric) The confirmations
#   "time" : ttt,             (numeric) The transaction time in seconds since epoch (Jan 1 1970 GMT)
#   "blocktime" : ttt         (numeric) The block time in seconds since epoch (Jan 1 1970 GMT)
# }
