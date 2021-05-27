all: ts.so

clean:
	rm ts.so

ts.so: libts
	cd libts && cargo build --release && mv target/release/libts.dylib ../ts.so && cd ..