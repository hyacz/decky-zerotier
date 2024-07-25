.PHONY: all
all: zerotier

zerotier-one:
	make zerotier-one -C zerotier

zerotier: zerotier-one
	mkdir -p ./out
	cp ./zerotier/zerotier-one ./out/

.PHONY: clean 
clean:
	make clean -C zerotier