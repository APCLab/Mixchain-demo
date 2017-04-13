BITCOIND=bitcoind -datadir=.
BITCOIN_CLI=bitcoin-cli -datadir=.

N ?= 1

run:
	${BITCOIND}

gen:
	${BITCOIN_CLI} generate ${N}

clean:
	rm -rv banlist.dat blocks/ chainstate/ db.log debug.log \
	       fee_estimates.dat peers.dat wallet.dat
