// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "base/test/scoped_feature_list.h"
#include "chrome/common/chrome_features.h"
#include "chrome/common/webui_url_constants.h"
#include "chrome/test/base/chrome_test_utils.h"
#include "chrome/test/base/in_process_browser_test.h"
#include "content/public/browser/render_frame_host.h"
#include "content/public/browser/web_contents.h"
#include "content/public/test/browser_test.h"
#include "content/public/test/browser_test_utils.h"
#include "content/public/test/test_utils.h"

namespace aimium {

class AimiumUIDisabledBrowserTest : public InProcessBrowserTest {
 public:
  AimiumUIDisabledBrowserTest() {
    scoped_feature_list_.InitAndDisableFeature(features::kAimium);
  }

 private:
  base::test::ScopedFeatureList scoped_feature_list_;
};

IN_PROC_BROWSER_TEST_F(AimiumUIDisabledBrowserTest, NotAvailable) {
  content::WebContents* web_contents =
      chrome_test_utils::GetActiveWebContents(this);
  EXPECT_FALSE(content::NavigateToURL(
      web_contents, content::GetWebUIURL(chrome::kChromeUIAimiumHost)));
  EXPECT_TRUE(web_contents->GetPrimaryMainFrame()->IsErrorDocument());
}

class AimiumUIBrowserTest : public InProcessBrowserTest {
 public:
  AimiumUIBrowserTest() {
    scoped_feature_list_.InitAndEnableFeature(features::kAimium);
  }

 private:
  base::test::ScopedFeatureList scoped_feature_list_;
};

IN_PROC_BROWSER_TEST_F(AimiumUIBrowserTest, LoadsFoundation) {
  content::WebContents* web_contents =
      chrome_test_utils::GetActiveWebContents(this);
  ASSERT_TRUE(content::NavigateToURL(
      web_contents, content::GetWebUIURL(chrome::kChromeUIAimiumHost)));
  EXPECT_FALSE(web_contents->GetPrimaryMainFrame()->IsErrorDocument());
  EXPECT_EQ("Aimium", content::EvalJs(web_contents, "document.title"));

  // Wait for the bundled module and its Lit template to render. This exercises
  // the resource pack, WebUI data source and TypeScript entry point together.
  EXPECT_EQ("Development foundation", content::EvalJs(web_contents, R"JS(
    (async () => {
      await customElements.whenDefined('aimium-app');
      const app = document.querySelector('aimium-app');
      await app.updateComplete;
      return app.shadowRoot.querySelector('#build-stage').textContent.trim();
    })();
  )JS"));
}

}  // namespace aimium
