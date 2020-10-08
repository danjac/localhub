import ActiveLinkController from './active-link-controller';
import AjaxController from './ajax-controller';
import AlertController from './alert-controller';
import AutoresizeController from './autoresize-controller';
import CalendarController from './calendar-controller';
import ClipboardController from './clipboard-controller';
import ConfirmDialogController from './confirm-dialog-controller';
import DropdownController from './dropdown-controller';
import FormController from './form-controller';
import HovercardController from './hovercard-controller';
import ImagePreviewController from './image-preview-controller';
import LinkifyController from './linkify-controller';
import MapController from './map-controller';
import MarkdownController from './markdown-controller';
import NotificationsController from './notifications-controller';
import OembedController from './oembed-controller';
import OpengraphPreviewController from './opengraph-preview-controller';
import SearchController from './search-controller';
import SidebarController from './sidebar-controller';
import TabsController from './tabs-controller';
import ToastController from './toast-controller';
import ToggleController from './toggle-controller';
import TypeaheadController from './typeahead-controller';
import WebpushController from './webpush-controller';

export default {
  'active-link': ActiveLinkController,
  'confirm-dialog': ConfirmDialogController,
  'image-preview': ImagePreviewController,
  'opengraph-preview': OpengraphPreviewController,
  ajax: AjaxController,
  alert: AlertController,
  autoresize: AutoresizeController,
  calendar: CalendarController,
  clipboard: ClipboardController,
  dropdown: DropdownController,
  form: FormController,
  hovercard: HovercardController,
  linkify: LinkifyController,
  map: MapController,
  markdown: MarkdownController,
  notifications: NotificationsController,
  oembed: OembedController,
  search: SearchController,
  sidebar: SidebarController,
  tabs: TabsController,
  toast: ToastController,
  toggle: ToggleController,
  typeahead: TypeaheadController,
  webpush: WebpushController,
};
