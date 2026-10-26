"""End-to-end smoke test script validating complete application workflow."""
import os
import sys
import io
import time
import asyncio
from pathlib import Path
from PIL import Image
import httpx

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app, lifespan
from backend.app.core.config import settings

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


async def run_async_smoke_test():
    print(f"==================================================")
    print(f"  Starting End-to-End In-Process Smoke Test")
    print(f"==================================================")

    async with lifespan(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            # 1. Check Health & Readiness
            print("\n[1/8] Checking API Health and Readiness...")
            health_res = await client.get("/api/v1/health")
            assert health_res.status_code == 200, f"Healthcheck failed: {health_res.text}"
            print(f"  ✓ /api/v1/health: {health_res.json()}")

            ready_res = await client.get("/api/v1/ready")
            assert ready_res.status_code == 200, f"Readiness failed: {ready_res.text}"
            print(f"  ✓ /api/v1/ready: {ready_res.json()}")

            # 2. Check Model Info
            print("\n[2/8] Fetching Model Info...")
            info_res = await client.get("/api/v1/model/info")
            assert info_res.status_code == 200, f"Model info failed: {info_res.text}"
            info_data = info_res.json()
            print(f"  ✓ Model Version: {info_data.get('model_version')}")
            print(f"  ✓ Architecture: {info_data.get('architecture')}")
            print(f"  ✓ Total Classes: {info_data.get('num_classes')}")

            # 3. User Registration and Authentication
            print("\n[3/8] Testing User Registration & Authentication...")
            test_email = f"smoketest_farmer_{int(time.time())}@example.com"
            test_password = "SmokeTestPassword123!"

            reg_res = await client.post(
                "/api/v1/auth/register",
                json={"email": test_email, "password": test_password, "full_name": "Smoke Test Farmer"}
            )
            assert reg_res.status_code == 201, f"Registration failed: {reg_res.text}"
            print(f"  ✓ Registered test user: {test_email}")

            login_res = await client.post(
                "/api/v1/auth/login",
                json={"email": test_email, "password": test_password}
            )
            assert login_res.status_code == 200, f"Login failed: {login_res.text}"
            token_data = login_res.json()
            access_token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            print("  ✓ Authenticated and obtained JWT access token")

            me_res = await client.get("/api/v1/auth/me", headers=headers)
            assert me_res.status_code == 200, f"Get /me failed: {me_res.text}"
            print(f"  ✓ Verified /me profile: {me_res.json()['email']}")

            # 4. Generate Synthetic Leaf Image for Upload
            print("\n[4/8] Submitting Leaf Image for Diagnostic Analysis...")
            leaf_img = Image.new("RGB", (256, 256), color=(40, 150, 40))
            buf = io.BytesIO()
            leaf_img.save(buf, format="JPEG", quality=90)
            buf.seek(0)

            files = {"image": ("test_leaf.jpg", buf.getvalue(), "image/jpeg")}
            data = {
                "latitude": "36.7468",
                "longitude": "-119.7726"
            }

            analyze_res = await client.post("/api/v1/analyze", files=files, data=data, headers=headers)
            assert analyze_res.status_code == 200, f"Analyze failed: {analyze_res.text}"
            analysis = analyze_res.json()
            analysis_id = analysis["id"]
            predicted_label = analysis["predicted_label"]
            confidence = analysis["confidence"]
            risk_level = analysis["risk_assessment"]["risk_level"]
            risk_score = analysis["risk_assessment"]["risk_score"]

            print(f"  ✓ Analysis ID: {analysis_id}")
            print(f"  ✓ Predicted Label: {predicted_label} (Confidence: {confidence:.2%})")
            print(f"  ✓ Outbreak Risk: {risk_level} (Score: {risk_score}/100)")
            print(f"  ✓ Top-3 Predictions: {[p['disease_name'] for p in analysis.get('top_k', [])]}")
            disease_details = analysis.get("disease_details") or {}
            print(f"  ✓ Prevention Steps: {len(disease_details.get('prevention_steps', []))} steps")
            print(f"  ✓ Sources: {disease_details.get('sources', [])}")

            # 5. Verify History Listing & Detail
            print("\n[5/8] Verifying Diagnosis History CRUD...")
            hist_res = await client.get("/api/v1/history", headers=headers)
            assert hist_res.status_code == 200, f"Get history failed: {hist_res.text}"
            history_items = hist_res.json()
            assert any(h["id"] == analysis_id for h in history_items), "Analysis ID not found in history list"
            print(f"  ✓ History list retrieved ({len(history_items)} items found)")

            detail_res = await client.get(f"/api/v1/history/{analysis_id}", headers=headers)
            assert detail_res.status_code == 200, f"Get history detail failed: {detail_res.text}"
            assert detail_res.json()["id"] == analysis_id
            print("  ✓ History detail retrieved and verified")

            # 6. Submit User Feedback
            print("\n[6/8] Submitting Farmer Feedback...")
            fb_res = await client.post(
                f"/api/v1/history/{analysis_id}/feedback",
                json={
                    "is_correct": True,
                    "comments": "E2E smoke test verification: symptoms match field observation.",
                    "consent_for_retraining": True
                },
                headers=headers
            )
            assert fb_res.status_code == 201, f"Feedback submission failed: {fb_res.text}"
            print("  ✓ Feedback recorded with retraining consent")

            # 7. Check Prometheus Metrics Endpoint
            print("\n[7/8] Verifying Prometheus Instrumentation Metrics...")
            metrics_res = await client.get("/metrics")
            assert metrics_res.status_code == 200, f"Metrics failed: {metrics_res.text}"
            assert "http_requests_total" in metrics_res.text or "http_request_duration_seconds" in metrics_res.text
            print("  ✓ Prometheus metrics endpoint active and collecting telemetry")

            # 8. Clean Up History & Account
            print("\n[8/8] Cleaning Up Smoke Test Artifacts...")
            del_hist = await client.delete(f"/api/v1/history/{analysis_id}", headers=headers)
            assert del_hist.status_code == 204, f"Delete history failed: {del_hist.text}"
            print("  ✓ History record deleted")

            del_user = await client.delete("/api/v1/auth/me", headers=headers)
            assert del_user.status_code == 204, f"Delete user failed: {del_user.text}"
            print("  ✓ Test user account deleted")

            print("\n==================================================")
            print("  ✅ ALL END-TO-END SMOKE TESTS PASSED SUCCESSFULLY!")
            print("==================================================")


if __name__ == "__main__":
    try:
        asyncio.run(run_async_smoke_test())
    except Exception as e:
        print(f"\n❌ E2E Smoke Test Failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
