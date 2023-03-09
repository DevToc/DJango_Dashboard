from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.urls import reverse_lazy
from .forms import ImportForm
from django.http import HttpResponse
import mimetypes
from django.contrib.auth.decorators import login_required

from .tasks import upload_file


@login_required(login_url="/login/")
def download_file(request, filename):
    # fill these variables with real values
    fileName = filename
    filePath = "./persistentLayer/temp/" + fileName
    fl_path = filePath  # ''
    fl = open(fl_path, "rb")
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response["Content-Disposition"] = "attachment; filename=%s" % filePath
    return response


class importExport(LoginRequiredMixin, View):

    template_name = "importExport/importExportMain.html"
    form_class = ImportForm
    success_url = reverse_lazy("import_export_main")

    def get(self, request, *args, **kwargs):
        context = {"form": self.form_class()}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        upload_file.delay(request)
        """
        except:
            context = {"form": self.form_class(
                request.POST, request.FILES)}
            return render(request, self.template_name, context)
        """
        successMessage = "Upload Successfull!"
        context = {"form": self.form_class(), "successMessage": successMessage}
        return render(request, self.template_name, context)

        # else:
        #     print("form is not valid")
        #     context = {"form": self.form_class(
        #         request.POST, request.FILES)}
        #     return render(request, self.template_name, context)
