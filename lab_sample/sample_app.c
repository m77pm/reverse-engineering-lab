// RE_LAB_SAMPLE_v1 - عينة مختبرية خاصة بالمشروع، للتعليم فقط
// Compile: gcc -O0 -o lab_sample/sample_app lab_sample/sample_app.c
#include <stdio.h>
#include <string.h>
const char *marker = "RE_LAB_SAMPLE_v1";
int is_admin(void) { return 0; } /* الهدف التعليمي: محلل يبحث عن هذه الدالة */
int main(void) {
    printf("Marker: %s\n", marker);
    if (is_admin())
        printf("Welcome Admin - All Permissions Granted\n");
    else
        printf("Access Denied - Normal User Mode\n");
    return 0;
}
