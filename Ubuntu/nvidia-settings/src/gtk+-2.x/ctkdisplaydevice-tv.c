/*
 * nvidia-settings: A tool for configuring the NVIDIA X driver on Unix
 * and Linux systems.
 *
 * Copyright (C) 2004 NVIDIA Corporation.
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms and conditions of the GNU General Public License,
 * version 2, as published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses>.
 */

/*
 * The TV DisplayDevice widget provides a way to adjust TV settings.
 */

#include <gtk/gtk.h>
#include <NvCtrlAttributes.h>

#include "ctkbanner.h"

#include "ctkdisplaydevice-tv.h"

#include "ctkimagesliders.h"
#include "ctkedid.h"
#include "ctkconfig.h"
#include "ctkhelp.h"
#include "ctkscale.h"
#include "ctkutils.h"
#include <stdio.h>
#define FRAME_PADDING 5


static const char* __tv_overscan_help = "The TV Overscan slider adjusts how "
"large the image is on the TV.";

static const char* __tv_flicker_filter_help = "The TV Flicker Filter slider "
"adjusts how much flicker filter is applied to the TV signal.";

static const char* __tv_brightness_help = "The TV Brightness slider adjusts "
"the brightness of the TV image.";

static const char* __tv_hue_help = "The TV Brightness slider adjusts "
"the hue of the TV image.";

static const char* __tv_contrast_help = "The TV Brightness slider adjusts "
"the contrast of the TV image.";

static const char* __tv_saturation_help = "The TV Brightness slider adjusts "
"the saturation of the TV image.";

static const char* __tv_refresh_rate_help = "The refresh rate displays the "
"rate at which the screen is currently refreshing the image.";

static const char* __tv_encoder_name_help = "The TV Encoder name displays "
"the name of TV Encoder.";

/* local prototypes */

static void ctk_display_device_tv_class_init(CtkDisplayDeviceTvClass *);
static void ctk_display_device_tv_finalize(GObject *);

static GtkWidget * add_scale(CtkDisplayDeviceTv *ctk_display_device_tv,
                             int attribute, char *name, const char *help);

static void adjustment_value_changed(GtkAdjustment *adjustment,
                                     gpointer user_data);

static void reset_button_clicked(GtkButton *button, gpointer user_data);

static void value_received(GtkObject *object, gpointer arg1,
                           gpointer user_data);

static void ctk_display_device_tv_setup(CtkDisplayDeviceTv
                                        *ctk_display_device_tv);

static void tv_info_setup(CtkDisplayDeviceTv *ctk_display_device_tv);

static void enabled_displays_received(GtkObject *object, gpointer arg1,
                                      gpointer user_data);
static void info_update_received(GtkObject *object, gpointer arg1,
                                 gpointer user_data);


GType ctk_display_device_tv_get_type(void)
{
    static GType ctk_display_device_tv_type = 0;
    
    if (!ctk_display_device_tv_type) {
        static const GTypeInfo ctk_display_device_tv_info = {
            sizeof (CtkDisplayDeviceTvClass),
            NULL, /* base_init */
            NULL, /* base_finalize */
            (GClassInitFunc) ctk_display_device_tv_class_init,
            NULL, /* class_finalize */
            NULL, /* class_data */
            sizeof (CtkDisplayDeviceTv),
            0, /* n_preallocs */
            NULL, /* instance_init */
            NULL  /* value_table */
        };

        ctk_display_device_tv_type = g_type_register_static (GTK_TYPE_VBOX,
                "CtkDisplayDeviceTv", &ctk_display_device_tv_info, 0);
    }

    return ctk_display_device_tv_type;
}

static void ctk_display_device_tv_class_init(
    CtkDisplayDeviceTvClass *ctk_display_device_tv_class
)
{
    GObjectClass *gobject_class = (GObjectClass *)ctk_display_device_tv_class;
    gobject_class->finalize = ctk_display_device_tv_finalize;
}

static void ctk_display_device_tv_finalize(
    GObject *object
)
{
    CtkDisplayDeviceTv *ctk_display_device_tv = CTK_DISPLAY_DEVICE_TV(object);
    g_free(ctk_display_device_tv->name);
    g_signal_handlers_disconnect_matched(ctk_display_device_tv->ctk_event,
                                         G_SIGNAL_MATCH_DATA,
                                         0,
                                         0,
                                         NULL,
                                         NULL,
                                         (gpointer) ctk_display_device_tv);
}


/*
 * ctk_display_device_tv_new() - constructor for the TV display
 * device page.
 */

GtkWidget* ctk_display_device_tv_new(NvCtrlAttributeHandle *handle,
                                     CtkConfig *ctk_config,
                                     CtkEvent *ctk_event,
                                     char *name)
{
    GObject *object;
    CtkDisplayDeviceTv *ctk_display_device_tv;
    GtkWidget *banner;
    GtkWidget *frame;
    GtkWidget *eventbox;
    GtkWidget *tmpbox;
    GtkWidget *hbox;
    GtkWidget *alignment;

    
    object = g_object_new(CTK_TYPE_DISPLAY_DEVICE_TV, NULL);
    if (!object) return NULL;
    
    ctk_display_device_tv = CTK_DISPLAY_DEVICE_TV(object);
    ctk_display_device_tv->handle = handle;
    ctk_display_device_tv->ctk_config = ctk_config;
    ctk_display_device_tv->ctk_event = ctk_event;
    ctk_display_device_tv->name = g_strdup(name);
    
    gtk_box_set_spacing(GTK_BOX(object), 10);
    
    /* banner */

    banner = ctk_banner_image_new(BANNER_ARTWORK_TV);
    gtk_box_pack_start(GTK_BOX(object), banner, FALSE, FALSE, 0);

    /* Information */

    frame = gtk_frame_new(NULL);
    gtk_box_pack_start(GTK_BOX(object), frame, FALSE, FALSE, 0);
    ctk_display_device_tv->info_frame = frame;
    
    hbox = gtk_hbox_new(FALSE, FRAME_PADDING);
    gtk_container_set_border_width(GTK_CONTAINER(hbox), FRAME_PADDING);
    gtk_container_add(GTK_CONTAINER(frame), hbox);
    
    tmpbox = gtk_vbox_new(FALSE, 5);
    gtk_container_add(GTK_CONTAINER(hbox), tmpbox);
    
    ctk_display_device_tv->txt_encoder_name = gtk_label_new("");
    ctk_display_device_tv->txt_refresh_rate = gtk_label_new("");
    
    /* pack the Refresh Rate Label */
    {
        typedef struct {
            GtkWidget *label;
            GtkWidget *txt;
            const gchar *tooltip;
        } TextLineInfo;

        TextLineInfo lines[] = {
            {
                gtk_label_new("TV Encoder:"),
                ctk_display_device_tv->txt_encoder_name,
                __tv_encoder_name_help,
            },
            {
                gtk_label_new("TV Refresh Rate:"),
                ctk_display_device_tv->txt_refresh_rate,
                __tv_refresh_rate_help,
            },
            { NULL, NULL, NULL }
        };
        
        int i;
        GtkRequisition req;
        int max_width;

        /* Compute max width of lables and setup text alignments */
        max_width = 0;
        for (i = 0; lines[i].label; i++) {
            gtk_misc_set_alignment(GTK_MISC(lines[i].label), 0.0f, 0.5f);
            gtk_misc_set_alignment(GTK_MISC(lines[i].txt), 0.0f, 0.5f);
            gtk_widget_size_request(lines[i].label, &req);
            
            if (max_width < req.width) {
                max_width = req.width;
            }
        }

        /* Pack labels */
        for (i = 0; lines[i].label; i++) {
            GtkWidget *tmphbox;

            /* Add separators */
            
            if (i == 1) {
                GtkWidget *separator = gtk_hseparator_new();
                gtk_box_pack_start(GTK_BOX(tmpbox), separator,
                                   FALSE, FALSE, 0);
            }
            /* Set the label's width */
            gtk_widget_set_size_request(lines[i].label, max_width, -1);
            /* add the widgets for this line */
            tmphbox = gtk_hbox_new(FALSE, 5);
            gtk_box_pack_start(GTK_BOX(tmphbox), lines[i].label,
                               FALSE, TRUE, 5);
            gtk_box_pack_start(GTK_BOX(tmphbox), lines[i].txt,
                               FALSE, TRUE, 5);

            /* Include tooltips */
            if (!lines[i].tooltip) {
                gtk_box_pack_start(GTK_BOX(tmpbox), tmphbox, FALSE, FALSE, 0);
            } else {
                eventbox = gtk_event_box_new();
                gtk_container_add(GTK_CONTAINER(eventbox), tmphbox);
                ctk_config_set_tooltip(ctk_config, eventbox, lines[i].tooltip);
                gtk_box_pack_start(GTK_BOX(tmpbox), eventbox, FALSE, FALSE, 0);
            }
        }
    }
    
    /* NV_CTRL_REFRESH_RATE */
    
    g_signal_connect(G_OBJECT(ctk_event),
                     CTK_EVENT_NAME(NV_CTRL_REFRESH_RATE),
                     G_CALLBACK(info_update_received),
                     (gpointer) ctk_display_device_tv);
    

    /* NV_CTRL_TV_OVERSCAN */

    ctk_display_device_tv->overscan =
        add_scale(ctk_display_device_tv, NV_CTRL_TV_OVERSCAN,
                  "TV OverScan", __tv_overscan_help);

    g_signal_connect(G_OBJECT(ctk_event),
                     CTK_EVENT_NAME(NV_CTRL_TV_OVERSCAN),
                     G_CALLBACK(value_received),
                     (gpointer) ctk_display_device_tv);
    
    /* NV_CTRL_TV_FLICKER_FILTER */

    ctk_display_device_tv->flicker_filter =
        add_scale(ctk_display_device_tv, NV_CTRL_TV_FLICKER_FILTER,
                  "TV Flicker Filter", __tv_flicker_filter_help);

    g_signal_connect(G_OBJECT(ctk_event),
                     CTK_EVENT_NAME(NV_CTRL_TV_FLICKER_FILTER),
                     G_CALLBACK(value_received),
                     (gpointer) ctk_display_device_tv);

    /* NV_CTRL_TV_BRIGHTNESS */

    ctk_display_device_tv->brightness =
        add_scale(ctk_display_device_tv, NV_CTRL_TV_BRIGHTNESS,
                  "TV Brightness", __tv_brightness_help);

    g_signal_connect(G_OBJECT(ctk_event),
                     CTK_EVENT_NAME(NV_CTRL_TV_BRIGHTNESS),
                     G_CALLBACK(value_received),
                     (gpointer) ctk_display_device_tv);

    /* NV_CTRL_TV_HUE */
    
    ctk_display_device_tv->hue =
        add_scale(ctk_display_device_tv, NV_CTRL_TV_HUE,
                  "TV Hue", __tv_hue_help);
    
    g_signal_connect(G_OBJECT(ctk_event),
                     CTK_EVENT_NAME(NV_CTRL_TV_HUE),
                     G_CALLBACK(value_received),
                     (gpointer) ctk_display_device_tv);

    /* NV_CTRL_TV_CONTRAST */
    
    ctk_display_device_tv->contrast =
        add_scale(ctk_display_device_tv, NV_CTRL_TV_CONTRAST,
                  "TV Contrast", __tv_contrast_help);

    g_signal_connect(G_OBJECT(ctk_event),
                     CTK_EVENT_NAME(NV_CTRL_TV_CONTRAST),
                     G_CALLBACK(value_received),
                     (gpointer) ctk_display_device_tv);

    /* NV_CTRL_TV_SATURATION */
    
    ctk_display_device_tv->saturation =
        add_scale(ctk_display_device_tv, NV_CTRL_TV_SATURATION,
                  "TV Saturation", __tv_saturation_help);
    
    g_signal_connect(G_OBJECT(ctk_event),
                     CTK_EVENT_NAME(NV_CTRL_TV_SATURATION),
                     G_CALLBACK(value_received),
                     (gpointer) ctk_display_device_tv);

    /* Create the reset button here so it can be used by the image sliders */

    ctk_display_device_tv->reset_button =
        gtk_button_new_with_label("Reset TV Hardware Defaults");
    
    /* create and pack the image sliders */
    
    ctk_display_device_tv->image_sliders =
        ctk_image_sliders_new(handle, ctk_config, ctk_event,
                              ctk_display_device_tv->reset_button,
                              name);
    if (ctk_display_device_tv->image_sliders) {
        gtk_box_pack_start(GTK_BOX(object),
                           ctk_display_device_tv->image_sliders,
                           FALSE, FALSE, 0);
    }
    
    /* reset button */

    g_signal_connect(G_OBJECT(ctk_display_device_tv->reset_button), "clicked",
                     G_CALLBACK(reset_button_clicked),
                     (gpointer) ctk_display_device_tv);
    
    alignment = gtk_alignment_new(1, 1, 0, 0);
    gtk_container_add(GTK_CONTAINER(alignment),
                      ctk_display_device_tv->reset_button);
    gtk_box_pack_end(GTK_BOX(object), alignment, TRUE, TRUE, 0);
    
    g_signal_connect(G_OBJECT(ctk_event),
                     CTK_EVENT_NAME(NV_CTRL_TV_RESET_SETTINGS),
                     G_CALLBACK(value_received),
                     (gpointer) ctk_display_device_tv);
    
    ctk_config_set_tooltip(ctk_config, ctk_display_device_tv->reset_button,
                           ctk_help_create_reset_hardware_defaults_text("TV", name));

    /* EDID button box */

    ctk_display_device_tv->edid =
        ctk_edid_new(ctk_display_device_tv->handle,
                     ctk_display_device_tv->ctk_config,
                     ctk_display_device_tv->ctk_event,
                     ctk_display_device_tv->name);

    hbox = gtk_hbox_new(FALSE, 0);
    gtk_box_pack_start(GTK_BOX(object), hbox, FALSE, FALSE, 0);
    gtk_box_pack_start(GTK_BOX(hbox), ctk_display_device_tv->edid,
                       TRUE, TRUE, 0);

    /* finally, display the widget */

    gtk_widget_show_all(GTK_WIDGET(object));

    /* update the GUI */

    update_display_enabled_flag(ctk_display_device_tv->handle,
                                &ctk_display_device_tv->display_enabled);

    ctk_display_device_tv_setup(ctk_display_device_tv);
    
    /* handle enable/disable events on the display device */

    g_signal_connect(G_OBJECT(ctk_event),
                     CTK_EVENT_NAME(NV_CTRL_ENABLED_DISPLAYS),
                     G_CALLBACK(enabled_displays_received),
                     (gpointer) ctk_display_device_tv);
    
    return GTK_WIDGET(object);
    
} /* ctk_display_device_tv_new() */



/*
 * Returns whether or not the scale is active
 */

static gint get_scale_active(CtkScale *scale)
{
    GtkAdjustment *adj = scale->gtk_adjustment;

    return
        GPOINTER_TO_INT(g_object_get_data(G_OBJECT(adj), "attribute active"));

} /* get_scale_active() */



/*
 * add_scale() - if the specified attribute exists and we can
 * query its valid values, create a new scale widget and pack it
 * in the ctk_display_device_tv
 */

static GtkWidget * add_scale(CtkDisplayDeviceTv *ctk_display_device_tv,
                             int attribute, char *name, const char *help)
{
    GtkObject *adj;
    GtkWidget *scale;

   
    adj = gtk_adjustment_new(0, 0, 10, 1, 1, 0);
        
    g_object_set_data(G_OBJECT(adj), "attribute",
                      GINT_TO_POINTER(attribute));

    g_object_set_data(G_OBJECT(adj), "attribute name", name);

    g_object_set_data(G_OBJECT(adj), "attribute active",
                      GINT_TO_POINTER(0));

    g_signal_connect(G_OBJECT(adj), "value_changed",
                     G_CALLBACK(adjustment_value_changed),
                     (gpointer) ctk_display_device_tv);
        
    scale = ctk_scale_new(GTK_ADJUSTMENT(adj), name,
                          ctk_display_device_tv->ctk_config,
                          G_TYPE_INT);
        
    if (help) {
        ctk_config_set_tooltip(ctk_display_device_tv->ctk_config,
                               CTK_SCALE_TOOLTIP_WIDGET(scale), help);
    }
    
    gtk_box_pack_start(GTK_BOX(ctk_display_device_tv), scale,
                       FALSE, FALSE, 0);
    
    return scale;

} /* add_scale() */



/*
 * post_adjustment_value_changed() - helper function for
 * adjustment_value_changed() and value_changed(); this does whatever
 * work is necessary after the adjustment has been updated --
 * currently, this just means posting a statusbar message.
 */

static void post_adjustment_value_changed(GtkAdjustment *adjustment,
                                          CtkDisplayDeviceTv
                                          *ctk_display_device_tv,
                                          gint value)
{
    char *name = g_object_get_data(G_OBJECT(adjustment), "attribute name");
    
    gtk_widget_set_sensitive(ctk_display_device_tv->reset_button, TRUE);

    ctk_config_statusbar_message(ctk_display_device_tv->ctk_config,
                                 "%s set to %d.", name, value);
    
} /* post_adjustment_value_changed() */



/*
 * adjustment_value_changed() - callback when any of the adjustments
 * in the CtkDisplayDeviceTv are changed: get the new value from the
 * adjustment, send it to the X server, and do any post-adjustment
 * work.
 */

static void adjustment_value_changed(GtkAdjustment *adjustment,
                                     gpointer user_data)
{
    CtkDisplayDeviceTv *ctk_display_device_tv =
        CTK_DISPLAY_DEVICE_TV(user_data);
    
    gint value;
    gint attribute;
    
    value = (gint) gtk_adjustment_get_value(adjustment);
    
    user_data = g_object_get_data(G_OBJECT(adjustment), "attribute");
    attribute = GPOINTER_TO_INT(user_data);

    NvCtrlSetAttribute(ctk_display_device_tv->handle,
                       attribute, (int) value);

    post_adjustment_value_changed(adjustment, ctk_display_device_tv, value);
    
} /* adjustment_value_changed() */



/*
 * reset_slider() - if the adjustment exists, query its current value
 * from the X server, and update the adjustment with the retrieved
 * value.
 */

static void reset_slider(CtkDisplayDeviceTv *ctk_display_device_tv,
                         GtkWidget *scale)
{
    GtkAdjustment *adj;
    gint attribute;
    ReturnStatus ret;
    gint val;

    adj = CTK_SCALE(scale)->gtk_adjustment;

    if (!adj) return;
    
    if (!get_scale_active(CTK_SCALE(scale))) return;

    attribute = GPOINTER_TO_INT(g_object_get_data(G_OBJECT(adj), "attribute"));

    ret = NvCtrlGetAttribute(ctk_display_device_tv->handle, attribute, &val);
    if (ret != NvCtrlSuccess) return;
    
    g_signal_handlers_block_matched(adj, G_SIGNAL_MATCH_FUNC, 0, 0, NULL,
                                    G_CALLBACK(adjustment_value_changed),
                                    NULL);

    gtk_adjustment_set_value(GTK_ADJUSTMENT(adj), val);
    
    g_signal_handlers_unblock_matched(adj, G_SIGNAL_MATCH_FUNC, 0, 0, NULL,
                                      G_CALLBACK(adjustment_value_changed),
                                      NULL);
} /* reset_slider() */



/*
 * reset_sliders() - reset all the adjustments and post a statusbar
 * message.
 */

static void reset_sliders(CtkDisplayDeviceTv *ctk_display_device_tv)
{
    /* retrieve all existing settings */

    reset_slider(ctk_display_device_tv, ctk_display_device_tv->overscan);
    reset_slider(ctk_display_device_tv, ctk_display_device_tv->flicker_filter);
    reset_slider(ctk_display_device_tv, ctk_display_device_tv->brightness);
    reset_slider(ctk_display_device_tv, ctk_display_device_tv->hue);
    reset_slider(ctk_display_device_tv, ctk_display_device_tv->contrast);
    reset_slider(ctk_display_device_tv, ctk_display_device_tv->saturation);

    ctk_config_statusbar_message(ctk_display_device_tv->ctk_config,
                                 "Reset TV Hardware defaults for %s.",
                                 ctk_display_device_tv->name);
} /* reset_sliders() */



/*
 * reset_button_clicked() - called when the "reset defaults" button is
 * pressed; tells the X server to reset its defaults, and then resets
 * all the sliders.
 */

static void reset_button_clicked(GtkButton *button, gpointer user_data)
{
    CtkDisplayDeviceTv *ctk_display_device_tv =
        CTK_DISPLAY_DEVICE_TV(user_data);
    gint active = 0;


    /* Disable the reset button here and allow the controls below to (re)enable
     * it if need be,.
     */
    gtk_widget_set_sensitive(ctk_display_device_tv->reset_button, FALSE);

    /* Make sure something is active */

    active =
        (get_scale_active(CTK_SCALE(ctk_display_device_tv->overscan)) ||
         get_scale_active(CTK_SCALE(ctk_display_device_tv->flicker_filter)) ||
         get_scale_active(CTK_SCALE(ctk_display_device_tv->brightness)) ||
         get_scale_active(CTK_SCALE(ctk_display_device_tv->hue)) ||
         get_scale_active(CTK_SCALE(ctk_display_device_tv->contrast)) ||
         get_scale_active(CTK_SCALE(ctk_display_device_tv->saturation)));

    if (active) {
        NvCtrlSetAttribute(ctk_display_device_tv->handle,
                           NV_CTRL_TV_RESET_SETTINGS, 1);
    }

    ctk_image_sliders_reset
        (CTK_IMAGE_SLIDERS(ctk_display_device_tv->image_sliders));

    reset_sliders(ctk_display_device_tv);

} /* reset_button_clicked() */



/*
 * value_received() - callback function for changed TV settings; this
 * is called when we receive an event indicating that another
 * NV-CONTROL client changed any of the settings that we care about.
 */

static void value_received(GtkObject *object, gpointer arg1,
                           gpointer user_data)
{
    CtkEventStruct *event_struct;
    CtkDisplayDeviceTv *ctk_display_device_tv =
        CTK_DISPLAY_DEVICE_TV(user_data);
    
    GtkAdjustment *adj;
    GtkWidget *scale;
    gint val;
    
    event_struct = (CtkEventStruct *) arg1;
    
    switch (event_struct->attribute) {
    case NV_CTRL_TV_OVERSCAN:
        scale = ctk_display_device_tv->overscan;
        break;
    case NV_CTRL_TV_FLICKER_FILTER:
        scale = ctk_display_device_tv->flicker_filter;
        break;
    case NV_CTRL_TV_BRIGHTNESS:
        scale = ctk_display_device_tv->brightness;
        break;
    case NV_CTRL_TV_HUE:
        scale = ctk_display_device_tv->hue;
        break;
    case NV_CTRL_TV_CONTRAST:
        scale = ctk_display_device_tv->contrast;
        break;
    case NV_CTRL_TV_SATURATION:
        scale = ctk_display_device_tv->saturation;
        break;
    case NV_CTRL_TV_RESET_SETTINGS:
        reset_sliders(ctk_display_device_tv);
        ctk_display_device_tv_setup(ctk_display_device_tv);
        return;
    default:
        return;
    }
    
    adj = CTK_SCALE(scale)->gtk_adjustment;
    val = gtk_adjustment_get_value(GTK_ADJUSTMENT(adj));

    if (val != event_struct->value) {
        
        val = event_struct->value;

        g_signal_handlers_block_by_func(adj, adjustment_value_changed,
                                        ctk_display_device_tv);
        
        gtk_adjustment_set_value(GTK_ADJUSTMENT(adj), val);
        
        post_adjustment_value_changed(GTK_ADJUSTMENT(adj),
                                      ctk_display_device_tv, val);
        
        g_signal_handlers_unblock_by_func(adj, adjustment_value_changed,
                                          ctk_display_device_tv);
    }
} /* value_received() */



/*
 * ctk_display_device_tv_create_help() - generate the help TextBuffer
 * for the TV DisplayDevice.
 */

GtkTextBuffer *ctk_display_device_tv_create_help(GtkTextTagTable *table,
                                                 CtkDisplayDeviceTv
                                                 *ctk_display_device_tv)
{
    GtkTextIter i;
    GtkTextBuffer *b;
    GtkTooltipsData *td;

    b = gtk_text_buffer_new(table);
    
    gtk_text_buffer_get_iter_at_offset(b, &i, 0);

    ctk_help_title(b, &i, "%s Help", ctk_display_device_tv->name);

    ctk_help_heading(b, &i, "TV Overscan");
    ctk_help_para(b, &i, __tv_overscan_help);
    
    ctk_help_heading(b, &i, "TV Flicker Filter");
    ctk_help_para(b, &i, __tv_flicker_filter_help);
    
    ctk_help_heading(b, &i, "TV Brightness");
    ctk_help_para(b, &i, __tv_brightness_help);
    
    ctk_help_heading(b, &i, "TV Hue");
    ctk_help_para(b, &i, __tv_hue_help);
    
    ctk_help_heading(b, &i, "TV Contrast");
    ctk_help_para(b, &i, __tv_contrast_help);
    
    ctk_help_heading(b, &i, "TV Saturation");
    ctk_help_para(b, &i, __tv_saturation_help);
    
    ctk_help_heading(b, &i, "TV Encoder name");
    ctk_help_para(b, &i, __tv_encoder_name_help);
    
    ctk_help_heading(b, &i, "TV Refresh rate");
    ctk_help_para(b, &i, __tv_refresh_rate_help);
    
    add_image_sliders_help
        (CTK_IMAGE_SLIDERS(ctk_display_device_tv->image_sliders), b, &i);

    add_acquire_edid_help(b, &i);

    td = gtk_tooltips_data_get(GTK_WIDGET(ctk_display_device_tv->reset_button));
    ctk_help_reset_hardware_defaults (b, &i, td->tip_text);

    ctk_help_finish(b);

    return b;
    
} /* ctk_display_device_tv_create_help() */


/* Update GUI state of the scale to reflect current settings
 * on the X Driver.
 */

static void setup_scale(CtkDisplayDeviceTv *ctk_display_device_tv,
                        int attribute, GtkWidget *scale)
{
    ReturnStatus ret0, ret1;
    NVCTRLAttributeValidValuesRec valid;
    NvCtrlAttributeHandle *handle = ctk_display_device_tv->handle;
    int val;
    GtkAdjustment *adj = CTK_SCALE(scale)->gtk_adjustment;
    

    /* Read settings from X server */
    ret0 = NvCtrlGetValidAttributeValues(handle, attribute, &valid);

    ret1 = NvCtrlGetAttribute(handle, attribute, &val);

    if ((ret0 == NvCtrlSuccess) && (ret1 == NvCtrlSuccess) &&
        (valid.type == ATTRIBUTE_TYPE_RANGE)) {

        g_signal_handlers_block_by_func(adj, adjustment_value_changed,
                                        ctk_display_device_tv);

        adj->lower = valid.u.range.min;
        adj->upper = valid.u.range.max;
        gtk_adjustment_changed(GTK_ADJUSTMENT(adj));

        gtk_adjustment_set_value(GTK_ADJUSTMENT(adj), val);

        g_signal_handlers_unblock_by_func(adj, adjustment_value_changed,
                                          ctk_display_device_tv);

        g_object_set_data(G_OBJECT(adj), "attribute active",
                          GINT_TO_POINTER(1));

        gtk_widget_set_sensitive(scale, TRUE);
        gtk_widget_show(scale);
    } else {

        g_object_set_data(G_OBJECT(adj), "attribute active",
                          GINT_TO_POINTER(0));

        gtk_widget_set_sensitive(scale, FALSE);
        gtk_widget_hide(scale);
    }


} /* setup_scale() */



/*
 * Updates the display device TV page to reflect the current
 * configuration of the display device.
 */
static void ctk_display_device_tv_setup(CtkDisplayDeviceTv
                                        *ctk_display_device_tv)
{
    /* Disable the reset button here and allow the controls below to (re)enable
     * it if need be,.
     */
    gtk_widget_set_sensitive(ctk_display_device_tv->reset_button, FALSE);


    /* Update info */

    tv_info_setup(ctk_display_device_tv);

    /* update acquire EDID button */

    ctk_edid_setup(CTK_EDID(ctk_display_device_tv->edid));


    /* Update controls */

    /* NV_CTRL_TV_OVERSCAN */

    setup_scale(ctk_display_device_tv, NV_CTRL_TV_OVERSCAN,
                ctk_display_device_tv->overscan);

    /* NV_CTRL_TV_FLICKER_FILTER */

    setup_scale(ctk_display_device_tv, NV_CTRL_TV_FLICKER_FILTER,
                ctk_display_device_tv->flicker_filter);

    /* NV_CTRL_TV_BRIGHTNESS */

    setup_scale(ctk_display_device_tv, NV_CTRL_TV_BRIGHTNESS,
                ctk_display_device_tv->brightness);

    /* NV_CTRL_TV_HUE */

    setup_scale(ctk_display_device_tv, NV_CTRL_TV_HUE,
                ctk_display_device_tv->hue);

    /* NV_CTRL_TV_CONTRAST */

    setup_scale(ctk_display_device_tv, NV_CTRL_TV_CONTRAST,
                ctk_display_device_tv->contrast);

    /* NV_CTRL_TV_SATURATION */

    setup_scale(ctk_display_device_tv, NV_CTRL_TV_SATURATION,
                ctk_display_device_tv->saturation);

    ctk_image_sliders_setup
        (CTK_IMAGE_SLIDERS(ctk_display_device_tv->image_sliders));

} /* ctk_display_device_tv_setup() */

static void tv_info_setup(CtkDisplayDeviceTv *ctk_display_device_tv)
{
    ReturnStatus ret;
    int val;
    char *str;
    
    /* NV_CTRL_STRING_TV_ENCODER_NAME */
    
    ret = NvCtrlGetStringDisplayAttribute(ctk_display_device_tv->handle, 0,
                                          NV_CTRL_STRING_TV_ENCODER_NAME,
                                          &str);
    if (ret == NvCtrlSuccess) {
        gtk_label_set_text(GTK_LABEL(ctk_display_device_tv->txt_encoder_name),
                           str);
        gtk_widget_show(ctk_display_device_tv->info_frame);
    } else {
        gtk_widget_hide(ctk_display_device_tv->info_frame);
    }

    /* NV_CTRL_REFRESH_RATE */

    ret = NvCtrlGetAttribute(ctk_display_device_tv->handle,
                             NV_CTRL_REFRESH_RATE,
                             &val);
    if (ret == NvCtrlSuccess) {
        float fvalue = ((float)(val)) / 100.0f;
        snprintf(str, 32, "%.2f Hz", fvalue);
        gtk_label_set_text(GTK_LABEL(ctk_display_device_tv->txt_refresh_rate),
                       str);
    } else {
        gtk_label_set_text
                 (GTK_LABEL(ctk_display_device_tv->txt_refresh_rate),
                  "Unknown");
    }
}

/*
 * When the list of enabled displays on the GPU changes,
 * this page should disable/enable access based on whether
 * or not the display device is enabled.
 */
static void enabled_displays_received(GtkObject *object, gpointer arg1,
                                      gpointer user_data)
{
    CtkDisplayDeviceTv *ctk_object = CTK_DISPLAY_DEVICE_TV(user_data);

    /* Requery display information only if display disabled */

    update_display_enabled_flag(ctk_object->handle,
                                &ctk_object->display_enabled);

    ctk_display_device_tv_setup(ctk_object);

} /* enabled_displays_received() */

/*
 * When GPU scaling activation and/or TV resolution changes occur,
 * we should update the GUI to reflect the current state.
 */
static void info_update_received(GtkObject *object, gpointer arg1,
                                 gpointer user_data)
{
    CtkDisplayDeviceTv *ctk_object = CTK_DISPLAY_DEVICE_TV(user_data);

    tv_info_setup(ctk_object);
}
