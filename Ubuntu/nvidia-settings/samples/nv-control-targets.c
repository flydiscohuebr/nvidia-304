/*
 * Copyright (c) 2006-2008 NVIDIA, Corporation
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice (including the next
 * paragraph) shall be included in all copies or substantial portions of the
 * Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */


/*
 * nv-control-targets.c - NV-CONTROL client that demonstrates how to
 * talk to various target types on an X Server (X Screens, GPU, FrameLock)
 */


#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <X11/Xlib.h>

#include "NVCtrl.h"
#include "NVCtrlLib.h"

#include "nv-control-screen.h"



/*
 * display_device_name() - return the display device name correspoding
 * to the display device mask.
 */

static char *display_device_name(int mask)
{
    switch (mask) {
    case (1 <<  0): return "CRT-0"; break;
    case (1 <<  1): return "CRT-1"; break;
    case (1 <<  2): return "CRT-2"; break;
    case (1 <<  3): return "CRT-3"; break;
    case (1 <<  4): return "CRT-4"; break;
    case (1 <<  5): return "CRT-5"; break;
    case (1 <<  6): return "CRT-6"; break;
    case (1 <<  7): return "CRT-7"; break;

    case (1 <<  8): return "TV-0"; break;
    case (1 <<  9): return "TV-1"; break;
    case (1 << 10): return "TV-2"; break;
    case (1 << 11): return "TV-3"; break;
    case (1 << 12): return "TV-4"; break;
    case (1 << 13): return "TV-5"; break;
    case (1 << 14): return "TV-6"; break;
    case (1 << 15): return "TV-7"; break;

    case (1 << 16): return "DFP-0"; break;
    case (1 << 17): return "DFP-1"; break;
    case (1 << 18): return "DFP-2"; break;
    case (1 << 19): return "DFP-3"; break;
    case (1 << 20): return "DFP-4"; break;
    case (1 << 21): return "DFP-5"; break;
    case (1 << 22): return "DFP-6"; break;
    case (1 << 23): return "DFP-7"; break;
    default: return "Unknown";
    }
} /* display_device_name() */



int main(int argc, char *argv[])
{
    Display *dpy;
    Bool ret;

    int major, minor;

    int num_gpus, num_screens, num_syncs;
    int num_vcs;
    int num_gvis;
    int num_coolers;
    int num_thermal_sensors;
    int gpu, screen;
    int display_devices, mask;
    int *pData;
    int len, j;
    char *str;

    
    
    /*
     * Open a display connection, and make sure the NV-CONTROL X
     * extension is present on the screen we want to use.
     */
    
    dpy = XOpenDisplay(NULL);
    if (!dpy) {
        fprintf(stderr, "Cannot open display '%s'.\n", XDisplayName(NULL));
        return 1;
    }

    screen = GetNvXScreen(dpy);

    ret = XNVCTRLQueryVersion(dpy, &major, &minor);
    if (ret != True) {
        fprintf(stderr, "The NV-CONTROL X extension does not exist on '%s'.\n",
                XDisplayName(NULL));
        return 1;
    }
    
    /* Print some information */

    printf("\n");
    printf("Using NV-CONTROL extension %d.%d on %s\n",
           major, minor, XDisplayName(NULL));


    /* Start printing server system information */

    printf("\n");
    printf("Server System Information:\n");
    printf("\n");


    /* Get the number of gpus in the system */

    ret = XNVCTRLQueryTargetCount(dpy, NV_CTRL_TARGET_TYPE_GPU, &num_gpus);
    if (!ret) {
        fprintf(stderr, "Failed to query number of gpus\n");
        return 1;
    }
    printf("  number of GPUs: %d\n", num_gpus);


    /* Get the number of X Screens in the system */

    ret = XNVCTRLQueryTargetCount(dpy, NV_CTRL_TARGET_TYPE_X_SCREEN,
                                  &num_screens);
    if (!ret) {
        fprintf(stderr, "Failed to query number of xscreens\n");
        return 1;
    }
    printf("  number of X Screens: %d\n", num_screens);


    /* Get the number of Frame Lock devices in the system */

    ret = XNVCTRLQueryTargetCount(dpy, NV_CTRL_TARGET_TYPE_FRAMELOCK,
                                  &num_syncs);
    if (!ret) {
        fprintf(stderr, "Failed to query number of xscreens\n");
        return 1;
    }
    printf("  number of Frame Lock Devices: %d\n", num_syncs);


    /* Get the number of Visual Computing System devices in
     * the system
     */

    ret = XNVCTRLQueryTargetCount(dpy, NV_CTRL_TARGET_TYPE_VCSC,
                                  &num_vcs);
    if (!ret) {
        fprintf(stderr, "Failed to query number of VCS\n");
        return 1;
    }
    printf("  number of Visual Computing System Devices: %d\n",
           num_vcs);


    /* Get the number of GVI devices in the system */

    ret = XNVCTRLQueryTargetCount(dpy, NV_CTRL_TARGET_TYPE_GVI,
                                  &num_gvis);
    if (!ret) {
        fprintf(stderr, "Failed to query number of GVIs\n");
        return 1;
    }
    printf("  number of Graphics Video Input Devices: %d\n",
           num_gvis);


    /* Get the number of Cooler devices in the system */

    ret = XNVCTRLQueryTargetCount(dpy, NV_CTRL_TARGET_TYPE_COOLER,
                                  &num_coolers);
    if (!ret) {
        fprintf(stderr, "Failed to query number of Coolers\n");
        return 1;
    }
    printf("  number of Cooler Devices: %d\n",
           num_coolers);


    /* Get the number of Thermal Sensor devices in the system */

    ret = XNVCTRLQueryTargetCount(dpy, NV_CTRL_TARGET_TYPE_THERMAL_SENSOR,
                                  &num_thermal_sensors);
    if (!ret) {
        fprintf(stderr, "Failed to query number of Thermal Sensors\n");
        return 1;
    }
    printf("  number of Thermal Sensor Devices: %d\n",
           num_thermal_sensors);


    /* display information about all GPUs */

    for (gpu = 0; gpu < num_gpus; gpu++) {

        printf("\n\n");
        printf("GPU %d information:\n", gpu);


        /* GPU name */

        ret = XNVCTRLQueryTargetStringAttribute(dpy,
                                                NV_CTRL_TARGET_TYPE_GPU,
                                                gpu, // target_id
                                                0, // display_mask
                                                NV_CTRL_STRING_PRODUCT_NAME,
                                                &str);
        if (!ret) {
            fprintf(stderr, "Failed to query gpu product name\n");
            return 1;
        }
        printf("   Product Name                    : %s\n", str);

        
        /* Connected Display Devices on GPU */

        ret = XNVCTRLQueryTargetAttribute(dpy,
                                          NV_CTRL_TARGET_TYPE_GPU,
                                          gpu, // target_id
                                          0, // display_mask
                                          NV_CTRL_CONNECTED_DISPLAYS,
                                          &display_devices);
        if (!ret) {
            fprintf(stderr, "Failed to query connected displays\n");
            return 1;
        }
        printf("   Display Device Mask (Connected) : 0x%08x\n",
               display_devices);


        /* Enabled Display Devices on GPU */

        ret = XNVCTRLQueryTargetAttribute(dpy,
                                          NV_CTRL_TARGET_TYPE_GPU,
                                          gpu, // target_id
                                          0, // display_mask
                                          NV_CTRL_ENABLED_DISPLAYS,
                                          &display_devices);
        if (!ret) {
            fprintf(stderr, "Failed to query enabled displays\n");
            return 1;
        }
        printf("   Display Device Mask (Enabled)   : 0x%08x\n",
               display_devices);
         

        /* X Screens driven by this GPU */

        ret = XNVCTRLQueryTargetBinaryData
            (dpy,
             NV_CTRL_TARGET_TYPE_GPU,
             gpu, // target_id
             0, // display_mask
             NV_CTRL_BINARY_DATA_XSCREENS_USING_GPU,
             (unsigned char **) &pData,
             &len);
        if (!ret) {
            fprintf(stderr, "Failed to query list of X Screens\n");
            return 1;
        }
        printf("   Number of X Screens on GPU %d    : %d\n", gpu, pData[0]);


        /* List all X Screens on GPU */

        for (j = 1; j <= pData[0]; j++) {
            screen = pData[j];
            
            printf("\n");
            printf("   X Screen %d information:\n", screen);


            /* Connected Display Devices on X Screen */

            ret = XNVCTRLQueryTargetAttribute(dpy,
                                              NV_CTRL_TARGET_TYPE_X_SCREEN,
                                              screen, // target_id
                                              0, // display_mask
                                              NV_CTRL_CONNECTED_DISPLAYS,
                                              &display_devices);
            if (!ret) {
                fprintf(stderr, "Failed to query connected displays\n");
                XFree(pData);
                return 1;
            }
            printf("      Display Device Mask (Connected) : 0x%08x\n",
                   display_devices);
            

            /* Enabled Display Devices on X Screen */

            ret = XNVCTRLQueryTargetAttribute(dpy,
                                              NV_CTRL_TARGET_TYPE_X_SCREEN,
                                              screen, // target_id
                                              0, // display_mask
                                              NV_CTRL_ENABLED_DISPLAYS,
                                              &display_devices);
            if (!ret) {
                fprintf(stderr, "Failed to query enabled displays\n");
                XFree(pData);
                return 1;
            }
            printf("      Display Device Mask (Enabled)   : 0x%08x\n",
                   display_devices);
            

            /* List all display devices on this X Screen */

            for (mask = 1; mask < (1 << 24); mask <<= 1) {
                if (!(display_devices & mask)) {
                    continue;
                }

                ret = XNVCTRLQueryTargetStringAttribute
                    (dpy,
                     NV_CTRL_TARGET_TYPE_X_SCREEN,
                     screen, // target_id
                     mask, // display_mask
                     NV_CTRL_STRING_DISPLAY_DEVICE_NAME,
                     &str);
                printf("      Display Device (0x%08x) : %s - '%s'\n",
                       mask,
                       display_device_name(mask),
                       str);
            }
        }
        XFree(pData);
    }

    return 0;
}
