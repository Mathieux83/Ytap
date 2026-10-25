import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import Mock, patch

from ytap import utils


class UtilsTests(unittest.TestCase):
    @patch("ytap.utils.requests.get")
    @patch("ytap.utils.load_api_key", return_value="test-key")
    def test_search_uses_mock_api_response(self, _api_key, get):
        get.return_value.json.return_value = {
            "items": [
                {
                    "id": {"videoId": "video-id"},
                    "snippet": {"title": 'Title with "quotes" and café'},
                }
            ]
        }
        self.assertEqual(
            utils.search_youtube("test"),
            [("video-id", 'Title with "quotes" and café')],
        )
        self.assertEqual(get.call_args.kwargs["params"]["key"], "test-key")

    @patch("ytap.utils.subprocess.run")
    @patch("ytap.utils.shutil.which", return_value="/usr/bin/fzf")
    def test_fzf_receives_options_as_stdin_without_shell(self, _which, run):
        options = 'Title with "quotes" and café (video-id)'
        run.return_value = Mock(returncode=0, stdout=options + "\n")
        self.assertEqual(utils.select_option(options, "Choose: "), "video-id")
        self.assertEqual(run.call_args.kwargs["input"], options)
        self.assertNotIn("shell", run.call_args.kwargs)

    @patch("builtins.input", return_value="1")
    @patch("ytap.utils.shutil.which", return_value=None)
    def test_numeric_selection_is_fallback_when_fzf_missing(self, _which, _input):
        self.assertEqual(utils.select_option("Title (video-id)", "Choose:"), "video-id")

    @patch("ytap.utils.shutil.which", return_value=None)
    def test_optional_player_detection_when_programs_are_missing(self, _which):
        self.assertFalse(utils.is_mpv_installed())
        with patch.dict("os.environ", {}, clear=True):
            self.assertFalse(utils.is_vlc_installed())

    @patch("ytap.utils.get_vlc_path", return_value=None)
    @patch("ytap.utils.shutil.which", return_value=None)
    def test_playback_reports_missing_player(self, _which, _vlc_path):
        output = StringIO()
        with redirect_stdout(output):
            self.assertFalse(utils.play_audio_with_mpv("video-id", "A song"))
            self.assertFalse(utils.play_audio_with_vlc("video-id", "A song"))
        self.assertIn("mpv is not installed", output.getvalue())
        self.assertIn("VLC is not installed", output.getvalue())

    @patch("ytap.utils.yt_dlp.YoutubeDL")
    def test_video_url_uses_yt_dlp_python_api(self, youtube_dl):
        downloader = youtube_dl.return_value.__enter__.return_value
        downloader.extract_info.return_value = {"url": "https://audio.example/stream"}
        self.assertEqual(utils.get_video_url("video-id"), "https://audio.example/stream")
        downloader.extract_info.assert_called_once_with(
            "https://www.youtube.com/watch?v=video-id",
            download=False,
        )

    @patch("builtins.input", return_value="y")
    @patch("ytap.utils.is_mpv_installed", return_value=True)
    @patch("ytap.utils.play_audio_with_mpv")
    @patch("ytap.utils.requests.get")
    @patch("ytap.utils.load_api_key", return_value="test-key")
    def test_playlist_passes_video_id_and_title_to_player(
        self, _api_key, get, play, _is_mpv, _input
    ):
        get.return_value.json.return_value = {
            "items": [
                {
                    "snippet": {
                        "title": "A song",
                        "resourceId": {"videoId": "video-id"},
                    }
                }
            ]
        }
        utils.play_playlist("playlist-id")
        play.assert_called_once_with("video-id", "A song", loop=False)

    @patch("ytap.utils.subprocess.run")
    @patch("ytap.utils.shutil.which", return_value="/usr/bin/fzf")
    def test_fzf_query_is_passed_without_a_shell(self, _which, run):
        run.return_value = Mock(returncode=1, stdout="A query\n")
        self.assertEqual(utils.get_search_query(), "A query")
        self.assertEqual(run.call_args.args[0][0], "/usr/bin/fzf")
        self.assertEqual(run.call_args.kwargs["input"], "")
        self.assertNotIn("shell", run.call_args.kwargs)


if __name__ == "__main__":
    unittest.main()
