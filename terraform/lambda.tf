resource "aws_lambda_function" "get_timeline" {
  function_name = "get-timeline"
  role          = aws_iam_role.timelines_lambda.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.timelines.repository_url}@${data.aws_ecr_image.timelines.image_digest}"

  environment {
    variables = {
      HTTP_METHOD = "GET"
    }
  }
}

resource "aws_lambda_function_url" "get_timeline" {
  function_name = aws_lambda_function.get_timeline.function_name
  authorization_type = "NONE"
}