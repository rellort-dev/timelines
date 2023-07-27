resource "aws_ecr_repository" "timelines" {
  name = "timelines"
}

data "aws_ecr_image" "timelines" {
  repository_name = aws_ecr_repository.timelines.name
  image_tag       = "latest"
}
