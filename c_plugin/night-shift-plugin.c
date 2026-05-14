/*
 * night-shift-plugin.c
 *
 * Minimal XFCE panel plugin (.so) that:
 *   1. Registers as a native X-XFCE-Module panel plugin
 *   2. Displays a moon icon in the panel
 *   3. Spawns the Python GTK app (popup) when clicked
 *
 * Build:
 *   gcc -shared -fPIC -o libnightshift.so night-shift-plugin.c \
 *       $(pkg-config --cflags --libs libxfce4panel-2.0 gtk+-3.0)
 */

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <gtk/gtk.h>
#include <libxfce4panel/libxfce4panel.h>

#define PYTHON_PLUGIN "/usr/lib/xfce4/panel/plugins/night-shift-py"

typedef struct
{
    XfcePanelPlugin *plugin;
    GtkWidget       *button;
    GtkWidget       *image;
} NightShiftPlugin;

/* ── Forward declarations ─────────────────────────────────────────────────── */
static void night_shift_construct (XfcePanelPlugin *plugin);

/* ── Registration ─────────────────────────────────────────────────────────── */
XFCE_PANEL_PLUGIN_REGISTER (night_shift_construct);


/* ── Callbacks ────────────────────────────────────────────────────────────── */

static void
button_clicked (GtkWidget        *button,
                NightShiftPlugin *ns)
{
    /* Get the screen coordinates of the button to pass to the python script
     * so it knows where to position the popup. */
    GdkWindow *window = gtk_widget_get_window (button);
    gint x = 0, y = 0, width = 0, height = 0;
    
    if (window)
    {
        gdk_window_get_origin (window, &x, &y);
        GtkAllocation alloc;
        gtk_widget_get_allocation (button, &alloc);
        width = alloc.width;
        height = alloc.height;
    }

    /* Spawn the python script, passing the button geometry */
    gchar *cmd = g_strdup_printf ("%s --x %d --y %d --w %d --h %d", 
                                  PYTHON_PLUGIN, x, y, width, height);
    
    GError *error = NULL;
    if (!g_spawn_command_line_async (cmd, &error))
    {
        g_warning ("Night Shift: failed to spawn python app: %s", error->message);
        g_error_free (error);
    }
    g_free (cmd);
}

static void
night_shift_free (XfcePanelPlugin  *plugin,
                  NightShiftPlugin *ns)
{
    g_free (ns);
}

static gboolean
size_changed (XfcePanelPlugin  *plugin,
              gint              size,
              NightShiftPlugin *ns)
{
    /* Adjust icon size based on panel size */
    gint icon_size = size - 4; 
    if (icon_size < 16) icon_size = 16;
    
    gtk_image_set_pixel_size (GTK_IMAGE (ns->image), icon_size);
    return TRUE;
}

/* ── Plugin constructor ──────────────────────────────────────────────────── */

static void
night_shift_construct (XfcePanelPlugin *plugin)
{
    NightShiftPlugin *ns = g_new0 (NightShiftPlugin, 1);
    ns->plugin = plugin;

    /* Make the plugin occupy a small square size */
    xfce_panel_plugin_set_small (plugin, TRUE);

    /* Create the button */
    ns->button = xfce_panel_create_button ();
    gtk_widget_set_can_focus (ns->button, FALSE);
    gtk_widget_set_tooltip_text (ns->button, "Night Shift (Color Temperature)");
    
    /* Create the icon */
    ns->image = gtk_image_new_from_icon_name ("night-light-symbolic", GTK_ICON_SIZE_BUTTON);
    gtk_container_add (GTK_CONTAINER (ns->button), ns->image);
    
    /* Add button to panel */
    gtk_container_add (GTK_CONTAINER (plugin), ns->button);
    gtk_widget_show_all (ns->button);

    /* Connect signals */
    g_signal_connect (ns->button, "clicked",
                      G_CALLBACK (button_clicked), ns);
                      
    g_signal_connect (plugin, "free-data",
                      G_CALLBACK (night_shift_free), ns);
                      
    g_signal_connect (plugin, "size-changed",
                      G_CALLBACK (size_changed), ns);
}
