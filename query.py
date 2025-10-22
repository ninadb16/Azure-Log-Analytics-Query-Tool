QUERY_TEMPLATES = {

"query_1_errors_last_day": r'''AzureActivity | where Level == 'Error' | limit 10''',
            "query_2_heartbeats_summary": r'''Heartbeat | summarize LastHeartbeat = max(TimeGenerated) by Computer, ResourceId, _ResourceId | order by LastHeartbeat desc | limit 50''',
            "query_3_all_security_events": r'''SecurityEvent | where EventID == 4624 or EventID == 4625 | limit 50''',
            "AppRequests_10": r'''AppRequests| take 10''',
            "AppRequests_2": r'''AppRequests | take 2'''
}

CLIENT_ID="38dca57a-f823-4530-b1b9-d5a7b377b1e4"
CLIENT_SECRET="Amv8Q~o147Mpm.WlsiauKSP.hP8FB7eyeFFWXaQv"
TENANT_ID="bfd32ece-0900-4f00-a1c2-9e59cdf1a4dd" 