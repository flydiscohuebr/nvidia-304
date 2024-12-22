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

#include <stdlib.h>
#include <string.h>

#include <gtk/gtk.h>
#include <NvCtrlAttributes.h>

#include "msg.h"

#include "ctkutils.h"
#include "ctkhelp.h"
#include "ctkpowermizer.h"
#include "ctkbanner.h"



#define FRAME_PADDING 10
#define DEFAULT_UPDATE_POWERMIZER_INFO_TIME_INTERVAL 1000

static gboolean update_powermizer_info(gpointer);
static void update_powermizer_menu_info(gpointer);
static void powermizer_menu_changed(GtkOptionMenu*, gpointer);
static void update_powermizer_menu_event(GtkObject *object,
                                         gpointer arg1,
                                         gpointer user_data);

static const char *__adaptive_clock_help =
"The Adaptive Clocking status describes if this feature "
"is currently enabled in this GPU.";

static const char *__power_source_help =
"The Power Source indicates whether the machine "
"is running on AC or Battery power.";

static const char *__current_pcie_link_width_help =
"This is the current PCIe link width of the GPU, in number of lanes.";

static const char *__current_pcie_link_speed_help =
"This is the current PCIe link speed of the GPU, "
"in gigatransfers per second (GT/s).";

static const char *__performance_level_help =
"This indicates the current Performance Level of the GPU.";

static const char *__gpu_clock_freq_help =
"This indicates the current Graphics Clock frequency.";

static const char *__memory_clock_freq_help =
"This indicates the current Memory Clock frequency.";

static const char *__processor_clock_freq_help =
"This indicates the current Processor Clock frequency.";

static const char *__performance_levels_table_help =
"This indicates the Performance Levels available for the GPU.  Each "
"performance level is indicated by a Performance Level number, along with "
"the Graphics, Memory and Processor clocks for that level.  The currently active "
"performance level is shown in regular text.  All other performance "
"levels are shown in gray.";

static const char *__powermizer_menu_help =
"The Preferred Mode menu allows you to choose the preferred Performance "
"State for the GPU, provided the GPU has multiple Performance Levels.  "
"'Adaptive' mode allows the GPU clocks to be adjusted based on GPU "
"utilization.  'Prefer Maximum Performance' hints to the driver to prefer "
"higher GPU clocks, when possible.  If a single X server is running, the "
"mode selected in nvidia-settings is what the system will be using; if two or "
"more X servers are running, the behavior is undefined.";

GType ctk_powermizer_get_type(void)
{
    static GType ctk_powermizer_type = 0;

    if (!ctk_powermizer_type) {
        static const GTypeInfo ctk_powermizer_info = {
            sizeof (CtkPowermizerClass),
            NULL, /* base_init */
            NULL, /* base_finalize */
            NULL, /* constructor */
            NULL, /* class_finalize */
            NULL, /* class_data */
            sizeof (CtkPowermizer),
            0,    /* n_preallocs */
            NULL, /* instance_init */
            NULL  /* value_table */
        };

        ctk_powermizer_type =
            g_type_register_static(GTK_TYPE_VBOX, "CtkPowermizer",
                                   &ctk_powermizer_info, 0);
    }

    return ctk_powermizer_type;

} /* ctk_powermizer_get_type() */



typedef struct {
    gint perf_level;
    gint nvclock;
    gint memclock;
    gint processorclock;
} perfModeEntry, * perfModeEntryPtr;


static void apply_perf_mode_token(char *token, char *value, void *data)
{
    perfModeEntryPtr pEntry = (perfModeEntryPtr) data;

    if (!strcasecmp("perf", token)) {
        pEntry->perf_level = atoi(value);
    } else if (!strcasecmp("nvclock", token)) {
        pEntry->nvclock = atoi(value);
    } else if (!strcasecmp("memclock", token)) {
        pEntry->memclock = atoi(value);
    } else if (!strcasecmp("processorclock", token)) {
        pEntry->processorclock = atoi(value);
    } else {
        nv_warning_msg("Unknown Perf Mode token value pair: %s=%s",
                       token, value);
    }
}


static void update_perf_mode_table(CtkPowermizer *ctk_powermizer,
                                   gint perf_level)
{
    GtkWidget *table;
    GtkWidget *label;
    char *perf_modes = NULL;
    char *tokens;
    char tmp_str[24];
    perfModeEntry entry;
    gint ret;
    gint row_idx; /* Where to insert into the perf mode table */
    gboolean active;

    /* Since table cell management in GTK lacks, just remove and rebuild
     * the table from scratch.
     */
    
    /* Dump out the old table */

    ctk_empty_container(ctk_powermizer->performance_table_hbox);
    
    /* Generate a new table */

    table = gtk_table_new(1, 4, FALSE);
    gtk_table_set_row_spacings(GTK_TABLE(table), 3);
    gtk_table_set_col_spacings(GTK_TABLE(table), 15);
    gtk_container_set_border_width(GTK_CONTAINER(table), 5);

    gtk_box_pack_start(GTK_BOX(ctk_powermizer->performance_table_hbox),
                       table, FALSE, FALSE, 0);
    
    label = gtk_label_new("Performance Level");
    gtk_misc_set_alignment(GTK_MISC(label), 0.0f, 0.5f);
    gtk_table_attach(GTK_TABLE(table), label, 0, 1, 0, 1,
            GTK_FILL, GTK_FILL | GTK_EXPAND, 5, 0);

    label = gtk_label_new("Graphics Clock");
    gtk_misc_set_alignment(GTK_MISC(label), 0.0f, 0.5f);
    gtk_table_attach(GTK_TABLE(table), label, 1, 2, 0, 1,
            GTK_FILL, GTK_FILL | GTK_EXPAND, 5, 0);

    label = gtk_label_new("Memory Clock");
    gtk_misc_set_alignment(GTK_MISC(label), 0.0f, 0.5f);
    gtk_table_attach(GTK_TABLE(table), label, 2, 3, 0, 1,
            GTK_FILL, GTK_FILL | GTK_EXPAND, 5, 0);

    if (ctk_powermizer->processor_clock) {
        label = gtk_label_new("Processor Clock");
        gtk_misc_set_alignment(GTK_MISC(label), 0.0f, 0.5f);
        gtk_table_attach(GTK_TABLE(table), label, 3, 4, 0, 1,
                         GTK_FILL, GTK_FILL | GTK_EXPAND, 5, 0);
    }
    /* Get the current list of perf levels */

    ret = NvCtrlGetStringAttribute(ctk_powermizer->attribute_handle,
                                   NV_CTRL_STRING_PERFORMANCE_MODES,
                                   &perf_modes); 

    if (ret != NvCtrlSuccess) {
        gtk_widget_show_all(table);
        /* Bail */
        return;
    }

    /* Parse the perf levels and populate the table */

    row_idx = 1;
    for (tokens = strtok(perf_modes, ";");
         tokens;
         tokens = strtok(NULL, ";")) {

        /* Invalidate perf mode entry */
        entry.perf_level = -1;
        entry.nvclock = -1;
        entry.memclock = -1;
        entry.processorclock = -1;
        
        parse_token_value_pairs(tokens, apply_perf_mode_token,
                                &entry);
        
        /* Only add complete perf mode entries */
        if ((entry.perf_level != -1) &&
            (entry.nvclock != -1) &&
            (entry.memclock != -1)) {
            
            active = (entry.perf_level == perf_level);

            /* XXX Assume the perf levels are sorted by the server */

            gtk_table_resize(GTK_TABLE(table), row_idx+1, 4);

            g_snprintf(tmp_str, 24, "%d", entry.perf_level);
            label = gtk_label_new(tmp_str);
            gtk_widget_set_sensitive(label, active);
            gtk_misc_set_alignment(GTK_MISC(label), 0.0f, 0.5f);
            gtk_table_attach(GTK_TABLE(table), label, 0, 1, row_idx, row_idx+1,
                             GTK_FILL, GTK_FILL | GTK_EXPAND, 5, 0);

            g_snprintf(tmp_str, 24, "%d MHz", entry.nvclock);
            label = gtk_label_new(tmp_str);
            gtk_widget_set_sensitive(label, active);
            gtk_misc_set_alignment(GTK_MISC(label), 0.0f, 0.5f);
            gtk_table_attach(GTK_TABLE(table), label, 1, 2, row_idx, row_idx+1,
                             GTK_FILL, GTK_FILL | GTK_EXPAND, 5, 0);

            g_snprintf(tmp_str, 24, "%d MHz", entry.memclock);
            label = gtk_label_new(tmp_str);
            gtk_widget_set_sensitive(label, active);
            gtk_misc_set_alignment(GTK_MISC(label), 0.0f, 0.5f);
            gtk_table_attach(GTK_TABLE(table), label, 2, 3, row_idx, row_idx+1,
                             GTK_FILL, GTK_FILL | GTK_EXPAND, 5, 0);

            if (ctk_powermizer->processor_clock) {
                g_snprintf(tmp_str, 24, "%d MHz", entry.processorclock);
                label = gtk_label_new(tmp_str);
                gtk_widget_set_sensitive(label, active);
                gtk_misc_set_alignment(GTK_MISC(label), 0.0f, 0.5f);
                gtk_table_attach(GTK_TABLE(table), label, 3, 4, row_idx, row_idx+1,
                                 GTK_FILL, GTK_FILL | GTK_EXPAND, 5, 0);
            }
            row_idx++;
        } else {
            nv_warning_msg("Incomplete Perf Mode (perf=%d, nvclock=%d,"
                           " memclock=%d)",
                           entry.perf_level, entry.nvclock,
                           entry.memclock);
        }
    }

    gtk_widget_show_all(table);

    XFree(perf_modes);
}



static gboolean update_powermizer_info(gpointer user_data)
{
    gint power_source, adaptive_clock, perf_level;
    gint clockret, gpu_clock, memory_clock, processor_clock;

    CtkPowermizer *ctk_powermizer;
    NvCtrlAttributeHandle *handle;
    gint ret;
    gchar *s;

    ctk_powermizer = CTK_POWERMIZER(user_data);
    handle = ctk_powermizer->attribute_handle;

    ret = NvCtrlGetAttribute(handle, NV_CTRL_GPU_ADAPTIVE_CLOCK_STATE,
                             &adaptive_clock);
    if (ret != NvCtrlSuccess) { 
        return FALSE;
    }

    if (adaptive_clock == NV_CTRL_GPU_ADAPTIVE_CLOCK_STATE_ENABLED) {
        s = g_strdup_printf("Enabled");
    }
    else if (adaptive_clock == NV_CTRL_GPU_ADAPTIVE_CLOCK_STATE_DISABLED) {
        s = g_strdup_printf("Disabled");
    }
    else {
        s = g_strdup_printf("Error");
    }

    gtk_label_set_text(GTK_LABEL(ctk_powermizer->adaptive_clock_status), s);
    g_free(s);
 
    ret = NvCtrlGetAttribute(handle, NV_CTRL_GPU_CURRENT_CLOCK_FREQS, 
                             &clockret);
    if (ret != NvCtrlSuccess) {
        return FALSE;
    }

    memory_clock = clockret & 0x0000FFFF;
    gpu_clock = (clockret >> 16);
    
    s = g_strdup_printf("%d Mhz", gpu_clock);
    gtk_label_set_text(GTK_LABEL(ctk_powermizer->gpu_clock), s);
    g_free(s);

    s = g_strdup_printf("%d Mhz", memory_clock);
    gtk_label_set_text(GTK_LABEL(ctk_powermizer->memory_clock), s);
    g_free(s);

    if (ctk_powermizer->processor_clock) {
        ret = NvCtrlGetAttribute(handle,
                                 NV_CTRL_GPU_CURRENT_PROCESSOR_CLOCK_FREQS,
                                 &processor_clock);
        if (ret == NvCtrlSuccess) {
            s = g_strdup_printf("%d Mhz", processor_clock);
            gtk_label_set_text(GTK_LABEL(ctk_powermizer->processor_clock), s);
            g_free(s);
        }
    }
    
    ret = NvCtrlGetAttribute(handle, NV_CTRL_GPU_POWER_SOURCE, &power_source);
    if (ret != NvCtrlSuccess) {
        return FALSE;
    }

    if (power_source == NV_CTRL_GPU_POWER_SOURCE_AC) {
        s = g_strdup_printf("AC");
    }
    else if (power_source == NV_CTRL_GPU_POWER_SOURCE_BATTERY) {
        s = g_strdup_printf("Battery");
    }
    else {
        s = g_strdup_printf("Error");
    }

    gtk_label_set_text(GTK_LABEL(ctk_powermizer->power_source), s);
    g_free(s);

    if (ctk_powermizer->pcie_gen_queriable) {
        /* NV_CTRL_GPU_PCIE_CURRENT_LINK_WIDTH */
        s = get_pcie_link_width_string(handle,
                                       NV_CTRL_GPU_PCIE_CURRENT_LINK_WIDTH);
        gtk_label_set_text(GTK_LABEL(ctk_powermizer->link_width), s);
        g_free(s);

        /* NV_CTRL_GPU_PCIE_MAX_LINK_SPEED */
        s = get_pcie_link_speed_string(handle,
                                       NV_CTRL_GPU_PCIE_CURRENT_LINK_SPEED);
        gtk_label_set_text(GTK_LABEL(ctk_powermizer->link_speed), s);
        g_free(s);
    }

    ret = NvCtrlGetAttribute(handle, NV_CTRL_GPU_CURRENT_PERFORMANCE_LEVEL, 
                             &perf_level);
    if (ret != NvCtrlSuccess) {
        return FALSE;
    }

    s = g_strdup_printf("%d", perf_level);
    gtk_label_set_text(GTK_LABEL(ctk_powermizer->performance_level), s);
    g_free(s);

    /* update the perf table */

    update_perf_mode_table(ctk_powermizer, perf_level);
 
    return TRUE;
}

GtkWidget* ctk_powermizer_new(NvCtrlAttributeHandle *handle,
                              CtkConfig *ctk_config,
                              CtkEvent *ctk_event)
{
    GObject *object;
    CtkPowermizer *ctk_powermizer;
    GtkWidget *hbox, *hbox2, *vbox, *vbox2, *hsep, *table;
    GtkWidget *banner, *label, *menu, *menu_item;
    ReturnStatus ret;
    gint val;
    gint row = 0;
    gchar *s = NULL;
    gint tmp;
    gboolean processor_clock_available = FALSE;

    /* make sure we have a handle */

    g_return_val_if_fail(handle != NULL, NULL);
    
    /* check if this screen supports powermizer querying */

    ret = NvCtrlGetAttribute(handle, NV_CTRL_GPU_POWER_SOURCE, &val);
    if (ret != NvCtrlSuccess) {
        return NULL;
    }

    ret = NvCtrlGetAttribute(handle, NV_CTRL_GPU_CURRENT_PERFORMANCE_LEVEL, 
                             &val);
    if (ret != NvCtrlSuccess) {
        return NULL;
    }

    ret = NvCtrlGetAttribute(handle, NV_CTRL_GPU_ADAPTIVE_CLOCK_STATE, 
                             &val);
    if (ret != NvCtrlSuccess) {
        return NULL;
    }

    ret = NvCtrlGetAttribute(handle, NV_CTRL_GPU_CURRENT_CLOCK_FREQS, 
                             &val);
    if (ret != NvCtrlSuccess) {
        return NULL;
    }

    ret = NvCtrlGetAttribute(handle, NV_CTRL_GPU_CURRENT_PROCESSOR_CLOCK_FREQS, 
                             &val);
    if (ret == NvCtrlSuccess) {
        processor_clock_available = TRUE;
    }

    /* create the CtkPowermizer object */

    object = g_object_new(CTK_TYPE_POWERMIZER, NULL);
    
    ctk_powermizer = CTK_POWERMIZER(object);
    ctk_powermizer->attribute_handle = handle;
    ctk_powermizer->ctk_config = ctk_config;
    ctk_powermizer->pcie_gen_queriable = FALSE;

    /* NV_CTRL_GPU_PCIE_GENERATION */

    ret = NvCtrlGetAttribute(handle, NV_CTRL_GPU_PCIE_GENERATION, &tmp);
    if (ret == NvCtrlSuccess) {
        ctk_powermizer->pcie_gen_queriable = TRUE;
    }

    /* set container properties for the CtkPowermizer widget */

    gtk_box_set_spacing(GTK_BOX(ctk_powermizer), 5);

    /* banner */

    banner = ctk_banner_image_new(BANNER_ARTWORK_THERMAL);
    gtk_box_pack_start(GTK_BOX(object), banner, FALSE, FALSE, 0);

    vbox = gtk_vbox_new(FALSE, 5);
    gtk_box_pack_start(GTK_BOX(object), vbox, TRUE, TRUE, 0);

    hbox = gtk_hbox_new(FALSE, 0);
    gtk_box_pack_start(GTK_BOX(vbox), hbox, FALSE, FALSE, 0);

    label = gtk_label_new("PowerMizer Information");
    gtk_box_pack_start(GTK_BOX(hbox), label, FALSE, FALSE, 0);

    hsep = gtk_hseparator_new();
    gtk_box_pack_start(GTK_BOX(hbox), hsep, TRUE, TRUE, 5);

    table = gtk_table_new(21, 2, FALSE);
    gtk_box_pack_start(GTK_BOX(vbox), table, FALSE, FALSE, 0);
    gtk_table_set_row_spacings(GTK_TABLE(table), 3);
    gtk_table_set_col_spacings(GTK_TABLE(table), 15);
    gtk_container_set_border_width(GTK_CONTAINER(table), 10);

    /* Adaptive Clocking State */

    ctk_powermizer->adaptive_clock_status =
        add_table_row_with_help_text(table, ctk_config,
                                     __adaptive_clock_help,
                                     row++, //row
                                     0,  // column
                                     0.0f,
                                     0.5,
                                     "Adaptive Clocking:",
                                     0.0,
                                     0.5,
                                     NULL);

    /* spacing */
    row += 3;

    /* Clock Frequencies */


    ctk_powermizer->gpu_clock =
        add_table_row_with_help_text(table, ctk_config,
                                     __gpu_clock_freq_help,
                                     row++, //row
                                     0,  // column
                                     0.0f,
                                     0.5,
                                     "Graphics Clock:",
                                     0.0,
                                     0.5,
                                     NULL);

    ctk_powermizer->memory_clock =
        add_table_row_with_help_text(table, ctk_config,
                                     __memory_clock_freq_help,
                                     row++, //row
                                     0,  // column
                                     0.0f,
                                     0.5,
                                     "Memory Clock:",
                                     0.0,
                                     0.5,
                                     NULL);

    /* Processor clock */
    if (processor_clock_available) {
        ctk_powermizer->processor_clock =
            add_table_row_with_help_text(table, ctk_config,
                                         __processor_clock_freq_help,
                                         row++, //row
                                         0,  // column
                                         0.0f,
                                         0.5,
                                         "Processor Clock:",
                                         0.0,
                                         0.5,
                                         NULL);
    }
    /* spacing */
    row += 3;

    /* Power Source */
    ctk_powermizer->power_source =
        add_table_row_with_help_text(table, ctk_config,
                                     __power_source_help,
                                     row++, //row
                                     0,  // column
                                     0.0f,
                                     0.5,
                                     "Power Source:",
                                     0.0,
                                     0.5,
                                     NULL);
    /* spacing */
    row += 3;

    /* Current PCIe Link Width */
    if (ctk_powermizer->pcie_gen_queriable) {
        ctk_powermizer->link_width =
            add_table_row_with_help_text(table, ctk_config,
                                         __current_pcie_link_width_help,
                                         row++, //row
                                         0,  // column
                                         0.0f,
                                         0.5,
                                         "Current PCIe Link Width:",
                                         0.0,
                                         0.5,
                                         NULL);

        /* Current PCIe Link Speed */
        ctk_powermizer->link_speed =
            add_table_row_with_help_text(table, ctk_config,
                                         __current_pcie_link_speed_help,
                                         row++, //row
                                         0,  // column
                                         0.0f,
                                         0.5,
                                         "Current PCIe Link Speed:",
                                         0.0,
                                         0.5,
                                         NULL);
        /* spacing */
        row += 3;
    }

    /* Performance Level */
    ctk_powermizer->performance_level =
        add_table_row_with_help_text(table, ctk_config,
                                     __performance_level_help,
                                     row++, //row
                                     0,  // column
                                     0.0f,
                                     0.5,
                                     "Performance Level:",
                                     0.0,
                                     0.5,
                                     NULL);
    gtk_table_resize(GTK_TABLE(table), row, 2);

    /* Available Performance Level Title */

    hbox = gtk_hbox_new(FALSE, 0);
    gtk_box_pack_start(GTK_BOX(vbox), hbox, FALSE, FALSE, 0);

    label = gtk_label_new("Performance Levels");
    gtk_box_pack_start(GTK_BOX(hbox), label, FALSE, FALSE, 0);

    hsep = gtk_hseparator_new();
    gtk_box_pack_start(GTK_BOX(hbox), hsep, TRUE, TRUE, 5);

    /* Available Performance Level Table */

    hbox = gtk_hbox_new(FALSE, 0);
    gtk_box_pack_start(GTK_BOX(vbox), hbox, FALSE, FALSE, 0);
    ctk_powermizer->performance_table_hbox = hbox;

    /* Register a timer callback to update the temperatures */

    s = g_strdup_printf("PowerMizer Monitor (GPU %d)",
                        NvCtrlGetTargetId(handle));
    
    ctk_config_add_timer(ctk_powermizer->ctk_config,
                         DEFAULT_UPDATE_POWERMIZER_INFO_TIME_INTERVAL,
                         s,
                         (GSourceFunc) update_powermizer_info,
                         (gpointer) ctk_powermizer);
    g_free(s);

    /* PowerMizer Settings */

    hbox = gtk_hbox_new(FALSE, 0);
    gtk_box_pack_start(GTK_BOX(vbox), hbox, FALSE, FALSE, 0);

    vbox2 = gtk_vbox_new(FALSE, 5);
    gtk_box_pack_start(GTK_BOX(hbox), vbox2, TRUE, TRUE, 0);
    ctk_powermizer->box_powermizer_menu = vbox2;

    /* H-separator */

    hbox2 = gtk_hbox_new(FALSE, 0);
    gtk_box_pack_start(GTK_BOX(vbox2), hbox2, FALSE, FALSE, 0);

    label = gtk_label_new("PowerMizer Settings");
    gtk_box_pack_start(GTK_BOX(hbox2), label, FALSE, FALSE, 0);

    hsep = gtk_hseparator_new();
    gtk_box_pack_start(GTK_BOX(hbox2), hsep, TRUE, TRUE, 5);

    /* Specifying drop down list */

    menu = gtk_menu_new();

    menu_item = gtk_menu_item_new_with_label("Adaptive");
    gtk_menu_shell_append(GTK_MENU_SHELL(menu), menu_item);
    gtk_widget_show(menu_item);

    menu_item = gtk_menu_item_new_with_label("Prefer Maximum Performance");
    gtk_menu_shell_append(GTK_MENU_SHELL(menu), menu_item);
    gtk_widget_show(menu_item);

    ctk_powermizer->powermizer_menu = gtk_option_menu_new();
    gtk_option_menu_set_menu(GTK_OPTION_MENU(ctk_powermizer->powermizer_menu),
                             menu);
    update_powermizer_menu_info(ctk_powermizer);

    g_signal_connect(G_OBJECT(ctk_powermizer->powermizer_menu), "changed",
                     G_CALLBACK(powermizer_menu_changed),
                     (gpointer) ctk_powermizer);

    ctk_config_set_tooltip(ctk_config,
                           ctk_powermizer->powermizer_menu,
                           __powermizer_menu_help);

    /* Packing the drop down list */

    table = gtk_table_new(1, 2, FALSE);
    gtk_box_pack_start(GTK_BOX(vbox2), table, FALSE, FALSE, 0);
    gtk_table_set_row_spacings(GTK_TABLE(table), 3);
    gtk_table_set_col_spacings(GTK_TABLE(table), 15);
    gtk_container_set_border_width(GTK_CONTAINER(table), 5);

    hbox2 = gtk_hbox_new(FALSE, 0);
    gtk_table_attach(GTK_TABLE(table), hbox2, 0, 1, 0, 1,
                     GTK_FILL, GTK_FILL | GTK_EXPAND, 5, 0);
    label = gtk_label_new("Preferred Mode:");
    gtk_misc_set_alignment(GTK_MISC(label), 0.0f, 0.5f);
    gtk_box_pack_start(GTK_BOX(hbox2), label, FALSE, FALSE, 0);

    hbox2 = gtk_hbox_new(FALSE, 0);
    gtk_table_attach(GTK_TABLE(table), hbox2, 1, 2, 0, 1,
                     GTK_FILL, GTK_FILL | GTK_EXPAND, 5, 0);
    gtk_box_pack_start(GTK_BOX(hbox2),
                       ctk_powermizer->powermizer_menu,
                       FALSE, FALSE, 0);

    /* Updating the powermizer page */

    update_powermizer_info(ctk_powermizer);
    gtk_widget_show_all(GTK_WIDGET(ctk_powermizer));

    g_signal_connect(G_OBJECT(ctk_event),
                     CTK_EVENT_NAME(NV_CTRL_GPU_POWER_MIZER_MODE),
                     G_CALLBACK(update_powermizer_menu_event),
                     (gpointer) ctk_powermizer);

    return GTK_WIDGET(ctk_powermizer);
}

static void update_powermizer_menu_event(GtkObject *object,
                                         gpointer arg1,
                                         gpointer user_data)
{
    update_powermizer_menu_info(user_data);
}

static void update_powermizer_menu_info(gpointer user_data)
{
    CtkPowermizer *ctk_powermizer = CTK_POWERMIZER(user_data);
    gint powerMizerMode = NV_CTRL_GPU_POWER_MIZER_MODE_ADAPTIVE;
    NVCTRLAttributeValidValuesRec valid;
    ReturnStatus ret0, ret1;

    ret0 = NvCtrlGetValidAttributeValues(ctk_powermizer->attribute_handle,
                                         NV_CTRL_GPU_POWER_MIZER_MODE,
                                         &valid);

    ret1 = NvCtrlGetAttribute(ctk_powermizer->attribute_handle,
                              NV_CTRL_GPU_POWER_MIZER_MODE,
                              &powerMizerMode);

    if ((ret0 != NvCtrlSuccess) || (ret1 != NvCtrlSuccess)) {
        gtk_widget_hide(ctk_powermizer->box_powermizer_menu);
    } else {
        g_signal_handlers_block_by_func(G_OBJECT(ctk_powermizer->powermizer_menu),
                                        G_CALLBACK(powermizer_menu_changed),
                                        (gpointer) ctk_powermizer);

        gtk_option_menu_set_history(GTK_OPTION_MENU(ctk_powermizer->powermizer_menu),
                                    powerMizerMode);

        g_signal_handlers_unblock_by_func(G_OBJECT(ctk_powermizer->powermizer_menu),
                                          G_CALLBACK(powermizer_menu_changed),
                                          (gpointer) ctk_powermizer);

        gtk_widget_show(ctk_powermizer->box_powermizer_menu);
    }
}

static void powermizer_menu_changed(GtkOptionMenu *powermizer_menu,
                                    gpointer user_data)
{
    CtkPowermizer *ctk_powermizer;
    gint history, powerMizerMode = NV_CTRL_GPU_POWER_MIZER_MODE_ADAPTIVE;

    ctk_powermizer = CTK_POWERMIZER(user_data);

    history = gtk_option_menu_get_history(powermizer_menu);

    switch (history) {
    case 1:
        powerMizerMode = NV_CTRL_GPU_POWER_MIZER_MODE_PREFER_MAXIMUM_PERFORMANCE;
        break;
    case 0:
    default:
        powerMizerMode = NV_CTRL_GPU_POWER_MIZER_MODE_ADAPTIVE;
    }

    if (NvCtrlSuccess != NvCtrlSetAttribute(ctk_powermizer->attribute_handle,
                                            NV_CTRL_GPU_POWER_MIZER_MODE,
                                            powerMizerMode)) {
        return;
    }

    g_signal_handlers_block_by_func(G_OBJECT(ctk_powermizer->powermizer_menu),
                                    G_CALLBACK(powermizer_menu_changed),
                                    (gpointer) ctk_powermizer);

    gtk_option_menu_set_history(GTK_OPTION_MENU(ctk_powermizer->powermizer_menu),
                                powerMizerMode);

    g_signal_handlers_unblock_by_func(G_OBJECT(ctk_powermizer->powermizer_menu),
                                      G_CALLBACK(powermizer_menu_changed),
                                      (gpointer) ctk_powermizer);
}

GtkTextBuffer *ctk_powermizer_create_help(GtkTextTagTable *table,
                                          CtkPowermizer *ctk_powermizer)
{
    GtkTextIter i;
    GtkTextBuffer *b;
    gchar *s;

    b = gtk_text_buffer_new(table);
    
    gtk_text_buffer_get_iter_at_offset(b, &i, 0);

    ctk_help_title(b, &i, "PowerMizer Monitor Help");
    ctk_help_para(b, &i, "When SLI is enabled, this page is only exposed "
                  "on the master GPU, and changes here will apply to "
                  "all GPUs in the SLI group.");
    
    ctk_help_heading(b, &i, "Adaptive Clocking");
    ctk_help_para(b, &i, __adaptive_clock_help);

    ctk_help_heading(b, &i, "Clock Frequencies");
    if (ctk_powermizer->processor_clock) {
        s = "This indicates the GPU's current Graphics Clock, "
            "Memory Clock and Processor Clock frequencies.";
    } else {
        s = "This indicates the GPU's current Graphics Clock and "
            "Memory Clock frequencies.";
    }
    ctk_help_para(b, &i, s);

    ctk_help_heading(b, &i, "Power Source");
    ctk_help_para(b, &i, __power_source_help);

    if (ctk_powermizer->pcie_gen_queriable) {
        ctk_help_heading(b, &i, "Current PCIe link width");
        ctk_help_para(b, &i, __current_pcie_link_width_help);
        ctk_help_heading(b, &i, "Current PCIe link speed");
        ctk_help_para(b, &i, __current_pcie_link_speed_help);
    }

    ctk_help_heading(b, &i, "Performance Level");
    ctk_help_para(b, &i, __performance_level_help);

    ctk_help_heading(b, &i, "Performance Levels (Table)");
    ctk_help_para(b, &i, __performance_levels_table_help);

    ctk_help_heading(b, &i, "PowerMizer Settings");
    ctk_help_para(b, &i, __powermizer_menu_help);
    ctk_help_finish(b);

    return b;
}

void ctk_powermizer_start_timer(GtkWidget *widget)
{
    CtkPowermizer *ctk_powermizer = CTK_POWERMIZER(widget);

    /* Start the powermizer timer */

    ctk_config_start_timer(ctk_powermizer->ctk_config,
                           (GSourceFunc) update_powermizer_info,
                           (gpointer) ctk_powermizer);
}

void ctk_powermizer_stop_timer(GtkWidget *widget)
{
    CtkPowermizer *ctk_powermizer = CTK_POWERMIZER(widget);

    /* Stop the powermizer timer */

    ctk_config_stop_timer(ctk_powermizer->ctk_config,
                          (GSourceFunc) update_powermizer_info,
                          (gpointer) ctk_powermizer);
}
