#See https://aka.ms/containerfastmode to understand how Visual Studio uses this Dockerfile to build your images for faster debugging.

FROM mcr.microsoft.com/dotnet/sdk:7.0 AS build
WORKDIR /src

# Copy csproj and restore dependencies
COPY *.sln .
COPY SchedulingAssistant/*.csproj ./SchedulingAssistant/
RUN dotnet restore

# Copy everything else and build
COPY . .
WORKDIR /src/SchedulingAssistant
RUN dotnet publish -c Release -o /app/publish

# Build runtime image
FROM mcr.microsoft.com/dotnet/aspnet:7.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .

# Create directory for data
RUN mkdir -p /app/data/images

# Expose ports
EXPOSE 80
EXPOSE 443

ENTRYPOINT ["dotnet", "SchedulingAssistant.dll"]