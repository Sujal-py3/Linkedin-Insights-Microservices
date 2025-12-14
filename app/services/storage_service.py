import asyncio

class StorageService:
    async def upload_image(self, image_url: str) -> str:
        """
        Mock upload of image to S3.
        In a real app, we would download the image from 'image_url' 
        and upload to an S3 bucket, returning the S3 URL.
        """
        # await upload_to_s3(image_url)
        return "https://mock-s3-bucket.s3.amazonaws.com/images/mock_image.jpg"

storage_service = StorageService()
