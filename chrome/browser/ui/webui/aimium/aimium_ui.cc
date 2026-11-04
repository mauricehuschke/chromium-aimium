// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "chrome/browser/ui/webui/aimium/aimium_ui.h"

#include "base/feature_list.h"
#include "chrome/browser/profiles/profile.h"
#include "chrome/common/chrome_features.h"
#include "chrome/common/webui_url_constants.h"
#include "chrome/grit/aimium_resources.h"
#include "chrome/grit/aimium_resources_map.h"
#include "content/public/browser/web_ui_data_source.h"
#include "content/public/common/url_constants.h"
#include "ui/webui/webui_util.h"

namespace aimium {

AimiumUIConfig::AimiumUIConfig()
    : DefaultWebUIConfig(content::kChromeUIScheme, chrome::kChromeUIAimiumHost) {}

bool AimiumUIConfig::IsWebUIEnabled(content::BrowserContext* browser_context) {
  return base::FeatureList::IsEnabled(features::kAimium);
}

AimiumUI::AimiumUI(content::WebUI* web_ui) : ui::MojoWebUIController(web_ui) {
  content::WebUIDataSource* source = content::WebUIDataSource::CreateAndAdd(
      Profile::FromWebUI(web_ui), chrome::kChromeUIAimiumHost);
  webui::SetupWebUIDataSource(source, kAimiumResources, IDR_AIMIUM_AIMIUM_HTML);
}

AimiumUI::~AimiumUI() = default;

WEB_UI_CONTROLLER_TYPE_IMPL(AimiumUI)

}  // namespace aimium
