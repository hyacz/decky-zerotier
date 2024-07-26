.PHONY: all
all: zerotier

zerotier-one:
	make zerotier-one -C zerotier

zerotier: zerotier-one
	mkdir -p ./out
	cp ./zerotier/zerotier-one ./out/
	ln -sf zerotier-one ./out/zerotier-idtool
	ln -sf zerotier-one ./out/zerotier-cli

.PHONY: clean 
clean:
	make clean -C zerotier