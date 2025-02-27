using Amazon;
using Amazon.S3;
using Amazon.S3.Model;
using Microsoft.Extensions.Configuration;
using System;
using System.IO;
using System.Threading.Tasks;

namespace SchedulingAssistant.Services
{
    public interface IS3ImageService
    {
        Task<string> UploadImageAsync(int eventId, Stream imageStream, string contentType, string fileExtension);
        Task<bool> DeleteImageAsync(int eventId, string fileExtension);
        string GetImageUrl(int eventId, string fileExtension);
    }

    public class S3ImageService : IS3ImageService
    {
        private readonly IAmazonS3 _s3Client;
        private readonly string _bucketName;
        private readonly string _baseUrl;

        public S3ImageService(IConfiguration configuration)
        {
            var accessKey = configuration["AWS:AccessKey"];
            var secretKey = configuration["AWS:SecretKey"];
            var region = configuration["AWS:Region"];
            _bucketName = configuration["AWS:BucketName"];
            
            // Construct the base URL for the S3 bucket
            _baseUrl = configuration["AWS:BaseUrl"] ?? $"https://{_bucketName}.s3.{region}.amazonaws.com";
            
            _s3Client = new AmazonS3Client(accessKey, secretKey, RegionEndpoint.GetBySystemName(region));
        }

        public async Task<string> UploadImageAsync(int eventId, Stream imageStream, string contentType, string fileExtension)
        {
            var key = $"events/{eventId}.{fileExtension}";
            
            var putRequest = new PutObjectRequest
            {
                BucketName = _bucketName,
                Key = key,
                InputStream = imageStream,
                ContentType = contentType,
                CannedACL = S3CannedACL.PublicRead
            };

            await _s3Client.PutObjectAsync(putRequest);
            
            return GetImageUrl(eventId, fileExtension);
        }

        public async Task<bool> DeleteImageAsync(int eventId, string fileExtension)
        {
            var key = $"events/{eventId}.{fileExtension}";
            
            var deleteRequest = new DeleteObjectRequest
            {
                BucketName = _bucketName,
                Key = key
            };

            var response = await _s3Client.DeleteObjectAsync(deleteRequest);
            return response.HttpStatusCode == System.Net.HttpStatusCode.NoContent;
        }

        public string GetImageUrl(int eventId, string fileExtension)
        {
            return $"{_baseUrl}/events/{eventId}.{fileExtension}";
        }
    }
} 