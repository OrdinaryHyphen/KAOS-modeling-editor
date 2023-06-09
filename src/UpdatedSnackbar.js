import React from 'react';
import PropTypes from 'prop-types';
import CloseIcon from '@material-ui/icons/Close';
import IconButton from '@material-ui/core/IconButton';
import Snackbar from '@material-ui/core/Snackbar';
import SnackbarContent from '@material-ui/core/SnackbarContent';
import { withStyles } from '@material-ui/core/styles';
import withRoot from './withRoot';
import packageJSON from '../package.json';
import versions from './versions.json';
import graphvizVersions from './graphviz-versions.json';

const styles = theme => ({
  snackbar: {
    "display": "block",
    "margin-top": "72px",
    "max-width": "none",
    "width": "100%",
  },
  content: {
    "backgroundColor": theme.palette.secondary.dark,
    "max-width": "inherit",
    "width": "inherit",
  }
});

class UpdatedSnackbar extends React.Component {

  handleClose = () => {
    this.props.onUpdatedSnackbarClose();
  };

  render() {
    const { classes } = this.props;
    const version = packageJSON.version;
    const changelogHeaderId = (() => {
      if (versions[version] == null) {
        return version;
      }
      else {
        const releaseDate = versions[version].release_date;
        return version.replace(/\./g, '') + "---" + releaseDate;
      }
    })();
    const graphvizVersion = this.props.graphvizVersion;
    const graphvizReleaseDate = graphvizVersions[graphvizVersion].release_date;
    const graphvizChangelogHeaderId = graphvizVersion.replace(/\./g, '') + "-" + graphvizReleaseDate;
    return (
      <Snackbar
        className={classes.snackbar}
        open={true}
        onClose={this.handleSnackbarClose}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'center',
        }}
      >
        <SnackbarContent
          className={classes.content}
          aria-describedby="client-snackbar"
          message={
            <span id="message-id">
              The Graphviz Visual Editor has been updated to version
              {' '}
              <a
                href={"https://github.com/magjac/graphviz-visual-editor/blob/master/CHANGELOG.md#" + changelogHeaderId}
                target="_blank"
                rel="noreferrer noopener"
                style={{ "color": "white" }}
              >
                {version}
              </a>
              . The underlying Graphviz software
              {this.props.newGraphvizVersion && ` has been updated to `}
              {!this.props.newGraphvizVersion && ` is still `}
              version
              {' '}
              <a
                href={"https://gitlab.com/graphviz/graphviz/-/blob/main/CHANGELOG.md#" + graphvizChangelogHeaderId}
                target="_blank"
                rel="noreferrer noopener"
                style={{ "color": "white" }}
              >
                {graphvizVersion}
              </a>
              .
            </span>}
          action={[
            <IconButton
              key="close"
              aria-label="Close"
              color="inherit"
              className={classes.close}
              onClick={this.handleClose}
            >
              <CloseIcon />
            </IconButton>,
          ]
          }
        />
      </Snackbar >
    );
  }
}

UpdatedSnackbar.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withRoot(withStyles(styles)(UpdatedSnackbar));
