# app/api/controllers.py

import logging
from flask import Flask, jsonify, request, render_template
from app.services.azure_service import AzureService
from app.config import load_config
from app.auth.token_cache import AzureTokenCache

log = logging.getLogger(__name__)

def setup_controllers(app: Flask):
    config = load_config()
    token_cache = AzureTokenCache(config)
    azure_service = AzureService(config, token_cache)
    
    # ----------------------------------------------------
    # STEP 1: RENDER THE BASE HTML PAGE
    # ----------------------------------------------------
    @app.route('/')
    def index():
        """Renders the single-page application interface."""
        return render_template('index.html', query_ids=config.PREDEFINED_QUERIES.keys())

    # ----------------------------------------------------
    # STEP 2: ENDPOINT TO FETCH ALL WORKSPACES
    # ----------------------------------------------------
    @app.route('/api/workspaces/all', methods=['GET'])
    def get_all_workspaces():
        """Fetches all Log Analytics Workspaces across accessible subscriptions."""
        try:
            workspaces = azure_service.discover_all_workspaces()
            return jsonify(workspaces)
        except RuntimeError as e:
            return jsonify({"error": str(e)}), 500
        except Exception as e:
            log.error(f"Unhandled error in get_all_workspaces: {e}", exc_info=True)
            return jsonify({"error": "Internal server error during discovery."}), 500

    # ----------------------------------------------------
    # STEP 3: LOG ANALYTICS QUERY EXECUTION
    # ----------------------------------------------------
    @app.route('/api/query', methods=['POST'])
    def run_query():
        data = request.json
        
        required_fields = ['queryId', 'start', 'end', 'workspaceId']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields in request."}), 400
        
        query_id = data['queryId']
        workspace_id = data['workspaceId']
        start_time = data['start']
        end_time = data['end']

        if query_id not in config.PREDEFINED_QUERIES:
            return jsonify({"error": f"Invalid queryId: {query_id}"}), 400

        kql_query = config.PREDEFINED_QUERIES[query_id]

        try:
            results = azure_service.run_query(workspace_id, kql_query, start_time, end_time)
            return jsonify(results)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400 
        except RuntimeError as e:
            return jsonify({"error": str(e)}), 500
        except Exception as e:
            log.error(f"Unhandled error during query execution: {e}", exc_info=True)
            return jsonify({"error": "Failed to execute query.", "detail": str(e)}), 500
