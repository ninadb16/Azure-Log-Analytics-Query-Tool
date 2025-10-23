QUERY_TEMPLATES = {
            "AppRequests_10": r'''AppRequests| take 10''',
            "Top 10 Slowest Requests": r'''AppRequests | where DurationMs > 1000 | project TimeGenerated, OperationName, DurationMs, Url, Id, ResultCode, OperationId | order by DurationMs desc| take 10 '''
}
