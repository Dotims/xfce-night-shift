CFLAGS  = $(shell pkg-config --cflags libxfce4panel-2.0 gtk+-3.0)
LDFLAGS = $(shell pkg-config --libs   libxfce4panel-2.0 gtk+-3.0)

all: libnightshift.so

libnightshift.so: night-shift-plugin.c
	gcc -shared -fPIC -o $@ $< $(CFLAGS) $(LDFLAGS) \
	    -Wl,-soname,libnightshift.so

install: libnightshift.so
	sudo install -Dm755 libnightshift.so \
	    /usr/lib/xfce4/panel/plugins/libnightshift.so
	sudo install -Dm755 ../night-shift-py \
	    /usr/lib/xfce4/panel/plugins/night-shift-py
	sudo install -Dm644 ../night-shift.desktop \
	    /usr/share/xfce4/panel/plugins/night-shift.desktop
	sudo install -dm755 /usr/lib/night-shift
	sudo cp -r ../night_shift /usr/lib/night-shift/
	@echo ""
	@echo "Done. Run:  xfce4-panel -r"
	@echo "Then:  Panel Preferences → Items → Add → Night Shift"

clean:
	rm -f libnightshift.so
