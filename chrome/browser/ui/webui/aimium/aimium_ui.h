// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef CHROME_BROWSER_UI_WEBUI_AIMIUM_AIMIUM_UI_H_
#define CHROME_BROWSER_UI_WEBUI_AIMIUM_AIMIUM_UI_H_

#include "content/public/browser/webui_config.h"
#include "ui/webui/mojo_web_ui_controller.h"

namespace content {
class BrowserContext;
class WebUI;
}  // namespace content

namespace aimium {

class AimiumUI;

// WebUIConfig for the opt-in chrome://aimium development entry point.
class AimiumUIConfig : public content::DefaultWebUIConfig<AimiumUI> {
 public:
  AimiumUIConfig();

  bool IsWebUIEnabled(content::BrowserContext* browser_context) override;
};

class AimiumUI : public ui::MojoWebUIController {
 public:
  explicit AimiumUI(content::WebUI* web_ui);
  ~AimiumUI() override;

  AimiumUI(const AimiumUI&) = delete;
  AimiumUI& operator=(const AimiumUI&) = delete;

  WEB_UI_CONTROLLER_TYPE_DECL();
};

}  // namespace aimium

#endif  // CHROME_BROWSER_UI_WEBUI_AIMIUM_AIMIUM_UI_H_
