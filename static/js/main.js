$(document).ready(function () {
  $("#loading").hide();

  $("#predict-btn").click(() => {
    $("#loading").show();
    let uploadedImage = new FormData($("#upload-form")[0]);


    $.ajax({
      type: "POST",
      url: "/predict",
      data: uploadedImage,
      contentType: false,
      cache: false,
      processData: false,
      async: true,
      success: function (data) {
        $("#loading").hide();

        //content = "<button class='btn btn-danger'>Error</button>";
        //(data["status"] == "success") {
          content =
            "<p>Bird: <strong>" +
            data["bird"] +
            "</strong></p><p>Conservation Status: <strong>" +
            data["Cstatus"] +
            "</strong></p><p>Bird Common: <strong>" +
            data["birdCommon"] +
            "</strong></p><p>Bird Category: <strong>" +
            data["birdCat"] +
            "</strong></p><p>Bird Period: <strong>" +
            data["birdSeason"] +
            "</strong></p>";

          $("#imageWidget").attr("src", data["image"]);
          $("#imageWidget").show();
        //}

        $("#result").html(content);
        console.log(data);
      },
    });
  });
});
