all: musicbot.so

clean:
	rm musicbot.so

musicbot.so: libmusicbot
	cd libmusicbot && cargo build --release && mv target/release/libmusicbot.dylib ../musicbot.so && cd ..