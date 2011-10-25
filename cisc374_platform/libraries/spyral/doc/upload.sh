ssh rdeaton@ren.eecis.udel.edu "rm -r ./public_html/spyral"
scp -r _build/html rdeaton@ren.eecis.udel.edu:./public_html/spyral
