using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading.Tasks;

public class ApiService
{
    private readonly HttpClient _httpClient;

    public ApiService(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    public async Task<string> GenerateResponse(string input)
    {
        var response = await _httpClient.PostAsJsonAsync("http://127.0.0.1:8000/generate-response", new { input });

        if (response.IsSuccessStatusCode)
        {
            var result = await response.Content.ReadFromJsonAsync<OutputModel>();
            return result?.Output ?? "No response from API";
        }
        return "Error in API call";
    }

    public async Task<List<string>> GetSampleQueries()
    {
        var response = await _httpClient.PostAsync("http://127.0.0.1:8000/generate-sample-queries", null);

        if (response.IsSuccessStatusCode)
        {
            var result = await response.Content.ReadFromJsonAsync<List<string>>();
            return result ?? new List<string>();
        }
        return new List<string> { "Error fetching sample queries" };
    }
}

public class OutputModel
{
    public string Output { get; set; } = string.Empty;
}
