variable "replicas" {
  description = "Number of horizontally scaled container instances"
  type        = number
  default     = 2
  validation {
    condition     = var.replicas >= 1 && var.replicas <= 10
    error_message = "Replicas must be between 1 and 10."
  }
}
